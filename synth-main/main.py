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
            ModulatedVolume(ADSREnvelope(attack_duration=0.01,
                                        decay_duration=0.1,
                                        sustain_level=0.8,
                                        release_duration=0.3,
                                        sample_rate=sample_rate
                                        ))
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

def osc_simple(freq, amp, sample_rate):
    """
    Onda senoidal con envolvente ADSR:
    attack=10ms, decay=100ms, sustain=80%, release=300ms.
    """
    return iter(
        Chain(
            SineOscillator(freq=freq, amp=amp, sample_rate=sample_rate),
            ModulatedVolume(
                ADSREnvelope(
                    attack_duration=0.01,
                    decay_duration=0.1,
                    sustain_level=1.0,
                    release_duration=0.3,
                    sample_rate=sample_rate
                )
            )
        )
    )

from synth.components.oscillators.oscillators import WavetableOscillator
from synth.components.tables import SineTable, SawtoothTable

sine_table     = SineTable(2048)
sawtooth_table = SawtoothTable(2048)

def osc_wavetable(freq, amp, sample_rate):
    """
    Un wavetable oscillator + ADSR, listo para PolySynth.
    Usa sine_table que está en el scope exterior.
    """
    return iter(
        Chain(
            # 1) Wavetable base
            WavetableOscillator(
                wavetable   = sine_table,   # o sawtooth_table, o cualquier otra
                freq        = freq,
                amp         = amp,
                sample_rate = sample_rate
            ),
            # 2) Una envolvente para tener dinámica
            ModulatedVolume(
                ADSREnvelope(
                    attack_duration  = 0.005,
                    decay_duration   = 0.1,
                    sustain_level    = 0.7,
                    release_duration = 0.3,
                    sample_rate      = sample_rate
                )
            )
        )
    )


synth = PolySynth(
    port_name   = "Launchkey Mini MK4 37 MIDI 0", 
    amp_scale   = 1.0,
    max_amp     = 1.0,  
    num_samples = 256    
)

synth.play(osc_wavetable)



