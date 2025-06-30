import os
import numpy as np
from synth.player import PolySynth
from synth.components.oscillators.oscillators import WavetableOscillator
from synth.components.envelopes import ADSREnvelope
from synth.components.composers import Chain
from synth.components.modifiers import ModulatedVolume

# 1) Ruta a UNA de tus tablas .npy
table_path = r"C:\Users\florc\Desktop\synth-main\synth-main\wavetables\vocal_acoustic_000-063-100.npy"

# 2) Carga la tabla
wavetable = np.load(table_path)  # array 1D con valores en [-1,1]

# 3) Define tu osc_function usando esa tabla
def osc_from_npy(freq, amp, sample_rate):
    return iter(
        Chain(
            WavetableOscillator(
                wavetable   = wavetable,
                freq        = freq,
                amp         = amp,
                sample_rate = sample_rate
            ),
            # Opcional: añade un ADSR para suavizar ataques/releases
            ModulatedVolume(
                ADSREnvelope(
                    attack_duration  = 0.01,
                    decay_duration   = 0.1,
                    sustain_level    = 0.8,
                    release_duration = 0.3,
                    sample_rate      = sample_rate
                )
            )
        )
    )

# 4) Instancia y corre el PolySynth
if __name__ == "__main__":
    synth = PolySynth(
        port_name   = "Launchkey Mini MK4 37 MIDI 0",
        amp_scale   = 1.0,
        max_amp     = 1.0,
        sample_rate = 44100,
        num_samples = 256
    )
    print("Toca tu controlador para escuchar la wavetable…")
    synth.play(osc_from_npy)
