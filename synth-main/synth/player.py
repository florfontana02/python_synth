import time
import numpy as np
import mido
import pyaudio

class PolySynth:
    def __init__(
        self,
        port_name: str = "Launchkey Mini MK4 37 MIDI 0",
        amp_scale: float = 1.0,
        max_amp: float = 1.0,
        sample_rate: int = 44100,
        num_samples: int = 256
    ):
        # abrir midi
        available = mido.get_input_names()
        if port_name not in available:
            raise Exception(f"MIDI port «{port_name}» no encontrado. Disponible:\n{available}")
        self.inport = mido.open_input(port_name)

        self.num_samples = num_samples
        self.sample_rate = sample_rate
        self.amp_scale   = amp_scale
        self.max_amp     = max_amp

    def _init_stream(self, nchannels: int):
        self.stream = pyaudio.PyAudio().open(
            rate=self.sample_rate,
            channels=nchannels,
            format=pyaudio.paInt16,
            output=True,
            frames_per_buffer=self.num_samples,
            output_device_index=3 #indice de salida
        )



    def _get_samples(self, notes_dict):
            """
            notes_dict: {note: [osc_generator, released_flag]}
            Devuelve un array (num_samples, nchannels) en int16, soportando mono o estéreo.
            """
            N = self.num_samples
            # si no hay voces, silencio mono
            if not notes_dict:
                return np.zeros((N, 1), dtype=np.int16)

            # extraer bloques por voz
            blocks = []
            for osc, _ in notes_dict.values():
                # generar N muestras de este oscilador
                samp = [next(osc) for _ in range(N)]
                arr = np.array(samp)
                # si es mono (1D), convertir a (N,1); si es tupla/estéreo, np.array crea (N,2)
                if arr.ndim == 1:
                    arr = arr[:, None]
                blocks.append(arr)

            # mezclar voces (sumar en el eje 0)
            mix = np.sum(np.stack(blocks, axis=0), axis=0) * self.amp_scale

            # clippear y convertir a int16
            mix = np.clip(mix, -self.max_amp, self.max_amp)
            mix = (mix * 32767).astype(np.int16)
            return mix



    @staticmethod
    def midi_to_freq(note: int) -> float:
        """convierte nota MIDI a frecuencia en Hz."""
        return 440.0 * (2 ** ((note - 69) / 12.0))


    def play(self, osc_function, close: bool = False):
        """
        osc_function(freq, amp, sample_rate) -> iterable of float or tuple
        """
        # oscilador de prueba para saber #canales
        raw_test = osc_function(freq=440.0, amp=1.0, sample_rate=self.sample_rate)
        test     = iter(raw_test)
        has_trigger = hasattr(raw_test, "trigger_release")

        # averiguar si es mono o estéreo
        buf = self._get_samples({-1: [test, False]})
        nchannels = buf.shape[1]
        self._init_stream(nchannels)

        notes_dict = {}
        print("PolySynth corriendo… ctrl+c para salir")

        try:
            while True:
                # procesar todo el MIDI primero 
                for msg in self.inport.iter_pending():
                    if msg.type == 'note_on' and msg.velocity > 0:
                        freq    = self.midi_to_freq(msg.note)
                        raw_osc = osc_function(freq=freq,
                                               amp=msg.velocity/127.0,
                                               sample_rate=self.sample_rate)
                        osc_iter = iter(raw_osc)
                        notes_dict[msg.note] = [osc_iter, False]

                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        if msg.note in notes_dict:
                            if has_trigger:
                                notes_dict[msg.note][0].trigger_release()
                                notes_dict[msg.note][1] = True
                            else:
                                del notes_dict[msg.note]

                # limpiar voces que hayan terminado su release
                if has_trigger:
                    ended = [n for n,(osc,rel) in notes_dict.items()
                             if getattr(osc, "ended", False) and rel]
                    for n in ended:
                        del notes_dict[n]

                # generar UN bloque de audio (silencio o voces) ——
                out = self._get_samples(notes_dict)  # siempre devuelve (num_samples, nch)
                self.stream.write(out.tobytes())
        
        except KeyboardInterrupt:
            print("deteniendo PolySynth…")
            self.stream.close()
            if close:
                self.inport.close()
