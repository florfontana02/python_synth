from synth.player import PolySynth
from synth.components.oscillators.oscillators import SineOscillator,SquareOscillator,SawtoothOscillator,TriangleOscillator
from synth.components.envelopes import ADSREnvelope
from synth.components.modifiers import Panner,Clipper,ModulatedVolume,Volume,ModulatedPanner
from synth.components.composers import WaveAdder,Chain 
from synth.components.osc_functions import osc_dynamic_chord,osc_function1,osc_wavetable,osc_complex_chord,osc_sine_adsr, osc_triangle_pluck,osc_saw_brite,osc_wavetable,osc_wavetable_piano_simple



synth = PolySynth(
    port_name   = "Launchkey Mini MK4 37 MIDI 0", 
    amp_scale   = 1.0,
    max_amp     = 1.0,  
    num_samples = 256    
)

synth.play(osc_wavetable_piano_simple)




