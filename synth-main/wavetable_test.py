import numpy as np
from synth.player import PolySynth
from synth.components.oscillators.oscillators import WavetableOscillator
from synth.components.envelopes import ADSREnvelope
from synth.components.composers import Chain
from synth.components.modifiers import ModulatedVolume

# 1) Carga tu wavetable multicycle
wavetable = np.load(r"C:\Users\florc\Desktop\synth-main\synth-main\wavetables_multi\vocal_acoustic_000-063-100_x6cycles.npy")

# 2) Define tu osc_function
def osc_multi(freq, amp, sample_rate):
    return iter(
        Chain(
            WavetableOscillator(
                wavetable   = wavetable,
                freq        = freq,
                amp         = amp,
                sample_rate = sample_rate
            ),
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

# 3) Lanza el synth
if __name__ == "__main__":
    synth = PolySynth(num_samples=256, amp_scale=1.0, max_amp=1.0)
    synth.play(osc_multi)
