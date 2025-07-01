from synth.player import PolySynth
from synth.components.oscillators.oscillators import SineOscillator,SquareOscillator,SawtoothOscillator,TriangleOscillator, WavetableOscillator
from synth.components.envelopes import ADSREnvelope
from synth.components.modifiers import Panner,Clipper,ModulatedVolume,Volume,ModulatedPanner
from synth.components.composers import WaveAdder,Chain 
import numpy as np


wavetable = np.load(r"C:\Users\florc\Desktop\synth-main\wavetables_cycle\guitar_electronic_028-036-127_cycle.npy")

def osc_cycle(freq, amp, sample_rate):
    return iter(
      Chain(
        WavetableOscillator(
          wavetable=wavetable,
          freq=freq,
          amp=amp,
          sample_rate=sample_rate
        ),
        ModulatedVolume(ADSREnvelope(0.01,0.1,0.8,0.3,sample_rate))
      )
    )

synth = PolySynth(
    port_name   = "Launchkey Mini MK4 37 MIDI 0", 
    amp_scale   = 1.0,
    max_amp     = 1.0,  
    num_samples = 256    
)

synth.play(osc_cycle)
