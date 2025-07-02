from synth.player import PolySynth
from synth.components.oscillators.oscillators import SineOscillator,SquareOscillator,SawtoothOscillator,TriangleOscillator
from synth.components.envelopes import ADSREnvelope
from synth.components.modifiers import Panner,Clipper,ModulatedVolume,Volume,ModulatedPanner
from synth.components.composers import WaveAdder,Chain 
import numpy as np
from synth.player import PolySynth
from osc_functions import osc_wavetable
import osc_functions

CC_MAP = {
    1:  'mod_wheel',
    21: 'master_volume',
    22: 'filter_cutoff',
    23: 'adsr_attack',
    24: 'adsr_decay',
    25: 'adsr_sustain',
    26: 'adsr_release',
    27: 'wavetable_mix',
    # …
}


# main.py

class SynthParams:
    def __init__(self):
        self.mod_wheel      = 0.0
        self.master_volume  = 1.0
        self.filter_cutoff  = 5000.0  # Hz
        self.adsr_attack    = 0.01
        self.adsr_decay     = 0.1
        self.adsr_sustain   = 0.8
        self.adsr_release   = 0.3
        self.wavetable_mix  = 0.0
        # …



if __name__ == "__main__":
    params = SynthParams()

    osc_functions.params = params

    synth = PolySynth(
        port_name   = "Launchkey Mini MK4 37 MIDI 0",
        amp_scale   = 1.0,
        max_amp     = 1.0,
        sample_rate = 44100,
        num_samples = 256,
        cc_map      = CC_MAP,
        params      = params
    )

    synth.play(osc_wavetable)
