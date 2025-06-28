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
        num_samples: int = 64
    ):
        # 1) Abrir puerto MIDI con Mido
        available = mido.get_input_names()
        if port_name not in available:
            raise Exception(f"MIDI port «{port_name}» no encontrado. Disponible:\n{available}")
        self.inport = mido.open_input(port_name)

        # 2) Parámetros audio
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
            output_device_index=4 #indice de salida
        )

    def _get_samples(self, notes_dict):
        """
        notes_dict: {note: [osc_generator, released_flag]}
        Devuelve un array (num_samples, nchannels) en int16
        """
        # 1) Para cada muestra, sumar osciladores activos
        out = []
        for _ in range(self.num_samples):
            vals = [next(o[0]) for o in notes_dict.values()]
            out.append(sum(vals) * self.amp_scale)

        arr = np.array(out)
        # 2) Clip y escala a int16
        arr = np.clip(arr, -self.max_amp, self.max_amp)
        arr = (arr * 32767).astype(np.int16)
        # 3) Mono → (num_samples, 1)
        return arr.reshape(self.num_samples, 1)

    @staticmethod
    def midi_to_freq(note: int) -> float:
        """Convierte nota MIDI a frecuencia en Hz."""
        return 440.0 * (2 ** ((note - 69) / 12.0))

    def play(self, osc_function, close: bool = False):
        """
        osc_function(freq: float, amp: float, sample_rate: int) -> Oscillator instance
        """
        # 1) Construir un oscilador de prueba y convertirlo en iterator
        raw_test = osc_function(
            freq=440.0,
            amp=1.0,
            sample_rate=self.sample_rate
        )
        test = iter(raw_test)                    # ← aquí: inicializa _i, _p, _step…
        has_trigger = hasattr(raw_test, "trigger_release")

        # 2) Determinar canales usando la función _get_samples
        samples = self._get_samples({-1: [test, False]})
        nchannels = samples.shape[1]
        self._init_stream(nchannels)

        try:
            notes_dict = {}
            print("PolySynth corriendo… Ctrl+C para salir")
            while True:
                # A) Generar audio si hay voces
                if notes_dict:
                    out = self._get_samples(notes_dict)
                    self.stream.write(out.tobytes())

                # B) Leer mensajes MIDI pendientes
                for msg in self.inport.iter_pending():
                    if msg.type == 'note_on' and msg.velocity > 0:
                        freq = self.midi_to_freq(msg.note)
                        raw_osc = osc_function(
                            freq=freq,
                            amp=msg.velocity / 127.0,
                            sample_rate=self.sample_rate
                        )
                        osc = iter(raw_osc)          # ← inicializar el oscilador
                        notes_dict[msg.note] = [osc, False]

                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        if msg.note in notes_dict:
                            if has_trigger:
                                raw_osc = notes_dict[msg.note][0]
                                raw_osc.trigger_release()
                                notes_dict[msg.note][1] = True
                            else:
                                del notes_dict[msg.note]

                # C) Limpiar voces que terminaron release
                if has_trigger:
                    ended = [
                        n for n, (osc, released) in notes_dict.items()
                        if getattr(osc, "ended", False) and released
                    ]
                    for n in ended:
                        del notes_dict[n]

                # D) Evitar 100% CPU
                time.sleep(self.num_samples / self.sample_rate)

        except KeyboardInterrupt:
            print("Deteniendo PolySynth...")
            self.stream.close()
            if close:
                self.inport.close()