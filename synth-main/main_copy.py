from synth.player import PolySynth
from synth.components.oscillators.oscillators import SineOscillator,SquareOscillator,SawtoothOscillator,TriangleOscillator
from synth.components.envelopes import ADSREnvelope
from synth.components.modifiers import Panner,Clipper,ModulatedVolume,Volume,ModulatedPanner
from synth.components.composers import WaveAdder,Chain 


def osc_func(freq, amp, sample_rate):
    return SquareOscillator(freq=freq, amp=amp, sample_rate=sample_rate)

def osc_function1(freq, amp, sample_rate):
    return iter(
        Chain(
            TriangleOscillator(freq=freq, amp=amp, sample_rate=sample_rate),
            ModulatedPanner(
                SineOscillator(freq/100, phase=90, sample_rate=sample_rate)
            ),
            ModulatedVolume(ADSREnvelope(0.01, release_duration=0.001, sample_rate=sample_rate))
        )
    )

def osc_function2(freq, amp, sample_rate):
    return iter(
        Chain(
            WaveAdder(
                Chain(
                    SineOscillator(freq=freq+4, amp=amp, sample_rate=sample_rate),
                    Panner(0.3)
                ),
                Chain(
                    TriangleOscillator(freq=freq, amp=amp, sample_rate=sample_rate),
                    Panner(0.7)
                ),
                Chain(
                    SawtoothOscillator(freq=freq/2, amp=amp*0.1, sample_rate=sample_rate),
                    Panner()
                )
            ),
            ModulatedVolume(ADSREnvelope(0.01,0.2,0.9,0.001))
        )
    )

synth = PolySynth(port_name="Launchkey Mini MK4 37 MIDI 0", 
                  amp_scale=1,
                  max_amp=1,
                  num_samples=256)
synth.play(osc_function1)

# from synth.player import PolySynth
# from synth.components.envelopes import ADSREnvelope
# from synth.components.oscillators.oscillators import SineOscillator

# def osc_with_adsr(freq, amp, sample_rate):
#     raw_osc = SineOscillator(freq=freq, amp=amp, sample_rate=sample_rate)
#     raw_env = ADSREnvelope(0.01, 0.1, 0.7, 0.3, sample_rate=sample_rate)
#     osc = iter(raw_osc)
#     env = iter(raw_env)

#     def gen():
#         for a in env:            # itera hasta que release termine
#             yield next(osc) * a

#     g = gen()
#     g.trigger_release = raw_env.trigger_release
#     g.ended = False
#     return g


# synth = PolySynth(amp_scale=1.0, max_amp=1.0)  # subí el volumen también
# synth.play(osc_with_adsr)