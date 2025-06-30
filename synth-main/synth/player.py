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

    def _get_samples2(self, notes_dict):
        """
        notes_dict: {note: [osc_generator, released_flag]}
        devuelve un array (num_samples, nchannels) en int16
        """
        if not notes_dict:
            # si no hay voces, devuelvo silencio mono
            return np.zeros((self.num_samples, 1), dtype=np.int16)

        # lista de iteradores
        oscs = [o[0] for o in notes_dict.values()]

        # stack de voces y suma para cada muestra
        frames = []
        for _ in range(self.num_samples):
            samp = [next(osc) for osc in oscs]
            arr = np.stack(samp, axis=0)       # shape (n_voices,) or (n_voices, nch)
            summed = np.sum(arr, axis=0) * self.amp_scale
            frames.append(summed)

        # convierto a numpy
        out = np.vstack(frames)
        # si mono (shape (N,)), forzamos (N,1)
        if out.ndim == 1:
            out = out[:, None]

        # clip y pasar a int16
        out = np.clip(out, -self.max_amp, self.max_amp)
        out = (out * 32767).astype(np.int16)
        return out

    def _get_samples(self, notes_dict):
        N = self.num_samples
        oscs = [ osc for osc,_ in notes_dict.values() ]

        if not oscs:
            mix = np.zeros(N, dtype=float)
        else:
            # genero de una vez el bloque de N muestras para cada oscilador
            blocks = []
            for osc in oscs:
                # extrae N muestras seguidas
                block = np.fromiter((next(osc) for _ in range(N)), float)
                blocks.append(block)

            # apilo todos los bloques en un array (M voces × N muestras)
            stacked = np.stack(blocks, axis=0)    # shape (M, N)

            # sumo en el eje 0 → mezclo voces y escalo de una
            mix = np.sum(stacked, axis=0) * self.amp_scale  # shape (N,)

        # clip y convertir a int16
        mix = np.clip(mix, -self.max_amp, self.max_amp)
        buf = (mix * 32767).astype(np.int16)

        # asegurar forma (N,1) para mono
        return buf.reshape(N, 1)



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
