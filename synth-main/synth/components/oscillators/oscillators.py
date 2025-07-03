import math
import numpy as np
from .base_oscillator import Oscillator


class SineOscillator(Oscillator):
    def _post_freq_set(self):
        self._step = (2 * math.pi * self._f) / self._sample_rate

    def _post_phase_set(self):
        self._p = (self._p / 360) * 2 * math.pi

    def _initialize_osc(self):
        self._i = 0

    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a


class SquareOscillator(SineOscillator):
    def __init__(
        self,
        freq=440,
        phase=0,
        amp=1,
        sample_rate=44_100,
        wave_range=(-1, 1),
        threshold=0,
    ):
        super().__init__(freq, phase, amp, sample_rate, wave_range)
        self.threshold = threshold

    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if val < self.threshold:
            val = self._wave_range[0]
        else:
            val = self._wave_range[1]
        return val * self._a


class SawtoothOscillator(Oscillator):
    def _post_freq_set(self):
        self._period = self._sample_rate / self._f
        self._post_phase_set

    def _post_phase_set(self):
        self._p = ((self._p + 90) / 360) * self._period

    def _initialize_osc(self):
        self._i = 0

    def __next__(self):
        div = (self._i + self._p) / self._period
        val = 2 * (div - math.floor(0.5 + div))
        self._i = self._i + 1
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a


class TriangleOscillator(SawtoothOscillator):
    def __next__(self):
        div = (self._i + self._p) / self._period
        val = 2 * (div - math.floor(0.5 + div))
        val = (abs(val) - 0.5) * 2
        self._i = self._i + 1
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a


class WavetableOscillator(Oscillator):

    def __init__(self, wavetable, freq=440, phase=0, amp=1,
                 sample_rate=44100, wave_range=(-1, 1)):
        # wavetable: array-like de floats en [-1,1]
        super().__init__(freq=freq, phase=phase, amp=amp,
                         sample_rate=sample_rate, wave_range=wave_range)
        self.wavetable = np.asarray(wavetable, dtype=float)

    def _post_freq_set(self):
        # calcula cuántos índices de tabla avanzamos por cada muestra
        self._N    = len(self.wavetable)
        self._step = (self.freq * self._N) / self._sample_rate

    def _post_phase_set(self):
        # phase en grados → posición inicial en muestras
        self._pos = (self.phase / 360) * self._N

    def _initialize_osc(self):
        # asegura que pos esté inicializada
        try:
            _ = self._pos
        except AttributeError:
            # si no vino de post_phase_set
            self._pos = 0.0

    def __next__(self):
        # indices entero y siguiente, con wrap
        i0   = int(self._pos) % self._N
        i1   = (i0 + 1) % self._N
        frac = self._pos - int(self._pos)
        # interpolación lineal
        v0 = self.wavetable[i0]
        v1 = self.wavetable[i1]
        val = (1 - frac) * v0 + frac * v1

        # avanzar posición
        self._pos = (self._pos + self._step) % self._N

        # aplicar rango y amplitud
        if self._wave_range != (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self.amp

