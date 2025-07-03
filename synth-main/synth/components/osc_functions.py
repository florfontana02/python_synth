from synth.player import PolySynth
from synth.components.oscillators.oscillators import SineOscillator,SquareOscillator,SawtoothOscillator,TriangleOscillator
from synth.components.envelopes import ADSREnvelope
from synth.components.modifiers import Panner,Clipper,ModulatedVolume,Volume,ModulatedPanner
from synth.components.composers import WaveAdder,Chain 
from synth.components.oscillators.oscillators import WavetableOscillator
from synth.components.tables import SineTable, TriangleTable, SawtoothTable, SquareTable
import numpy as np


sine_table     = SineTable(2048)
triangle_table = TriangleTable(2048)
sawtooth_table = SawtoothTable(2048)
square_table   = SquareTable(2048)
wavetable1 = np.load(r"C:\Users\florc\Desktop\synth-main\wavetables_cycle\guitar_electronic_028-036-127_cycle.npy")
wavetable2 = np.load(r"C:\Users\florc\Desktop\synth-main\wavetables_cycle\vocal_acoustic_000-063-100_cycle.npy")
wavetable = np.load(r"C:\Users\florc\Desktop\synth-main\wavetables_cycle\keyboard_acoustic_004-049-075_cycle.npy")

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



sine_table     = SineTable(2048)
sawtooth_table = SawtoothTable(2048)

def osc_wavetable(freq, amp, sample_rate):
    """
    Un wavetable oscillator + ADSR, listo para PolySynth.
    Usa sine_table que está en el scope exterior.
    """
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
                    attack_duration  = 0.005,
                    decay_duration   = 0.1,
                    sustain_level    = 0.7,
                    release_duration = 0.3,
                    sample_rate      = sample_rate
                )
            )
        )
    )




FREQS = {
    "C4": 261.63,
    "E4": 329.63,
    "G4": 392.00,
    "B4": 493.88,
}

def osc_complex_chord(freq, amp, sample_rate):
    """
    Ignoramos freq/amp de la voz MIDI y tocamos un acorde fijo:
    C4, E4, G4, B4, cada uno con su wavetable y paneo LFO.
    """

    gen = WaveAdder(
        # Voz 1: C4 con tabla senoidal
        Chain(
            WavetableOscillator(
                wavetable   = sine_table,
                freq        = FREQS["C4"],
                amp         = 0.25,           # reducimos ganancia para no saturar al sumar
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq       = 3,          # 3 Hz LFO
                    wave_range = (-1,1),
                    sample_rate= sample_rate
                )
            )
        ),
        # Voz 2: E4 con tabla triangular
        Chain(
            WavetableOscillator(
                wavetable   = triangle_table,
                freq        = FREQS["E4"],
                amp         = 0.25,
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq       = 2,          # 2 Hz LFO
                    wave_range = (-1,1),
                    sample_rate= sample_rate
                )
            )
        ),
        # Voz 3: G4 con tabla sawtooth
        Chain(
            WavetableOscillator(
                wavetable   = sawtooth_table,
                freq        = FREQS["G4"],
                amp         = 0.25,
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq        = 3,
                    phase       = 180,      # desfase 180°
                    wave_range  = (-1,1),
                    sample_rate = sample_rate
                )
            )
        ),
        # Voz 4: B4 con tabla square
        Chain(
            WavetableOscillator(
                wavetable   = square_table,
                freq        = FREQS["B4"],
                amp         = 0.25,
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq        = 2,
                    phase       = 180,
                    wave_range  = (-1,1),
                    sample_rate = sample_rate
                )
            )
        ),

        stereo=True   # salida estereofónica
    )

    return iter(gen)


def osc_dynamic_chord(freq, amp, sample_rate):

    """
    Crea 4 voces en paralélo con la frecuencia 'freq' de la nota tocada,
    cada una con una tabla distinta y paneo LFO.
    amp viene de velocity/127; lo repartimos entre las voces.
    """

    voice_amp = amp * 0.25  # repartir ganancia

    gen = WaveAdder(
        # Voz 1: tabla senoidal
        Chain(
            WavetableOscillator(
                wavetable   = sine_table,
                freq        = freq,
                amp         = voice_amp,
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq        = 3,            # 3 Hz LFO
                    wave_range  = (-1,1),
                    sample_rate = sample_rate
                )
            )
        ),
        # Voz 2: tabla triangular
        Chain(
            WavetableOscillator(
                wavetable   = triangle_table,
                freq        = freq,
                amp         = voice_amp,
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq        = 2, 
                    wave_range  = (-1,1),
                    sample_rate = sample_rate
                )
            )
        ),
        # Voz 3: tabla sawtooth
        Chain(
            WavetableOscillator(
                wavetable   = sawtooth_table,
                freq        = freq,
                amp         = voice_amp,
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq        = 3,
                    phase       = 180,
                    wave_range  = (-1,1),
                    sample_rate = sample_rate
                )
            )
        ),
        # Voz 4: tabla square
        Chain(
            WavetableOscillator(
                wavetable   = square_table,
                freq        = freq,
                amp         = voice_amp,
                sample_rate = sample_rate
            ),
            ModulatedPanner(
                SineOscillator(
                    freq        = 2,
                    phase       = 180,
                    wave_range  = (-1,1),
                    sample_rate = sample_rate
                )
            )
        ),

        stereo=True
    )

    # iter(gen) arranca el iterador interno y lo devuelve
    return iter(gen)



def osc_sine_adsr(freq, amp, sample_rate):
    """
    Onda senoidal pura con ADSR suave:
    ataque 10 ms, decay 200 ms, sustain 50 %, release 500 ms.
    """
    return iter(
        Chain(
            WavetableOscillator(
                wavetable   = sine_table,
                freq        = freq,
                amp         = amp,
                sample_rate = sample_rate
            ),
            ModulatedVolume(
                ADSREnvelope(
                    attack_duration  = 0.01,
                    decay_duration   = 0.2,
                    sustain_level    = 0.5,
                    release_duration = 0.5,
                    sample_rate      = sample_rate
                )
            )
        )
    )

# ————————————————
def osc_triangle_pluck(freq, amp, sample_rate):
    """
    Onda triangular con pluck rápido:
    ataque 5 ms, decay 50 ms, sustain 0 (percusión), release 100 ms.
    Ideal para sonidos percusivos.
    """
    return iter(
        Chain(
            WavetableOscillator(
                wavetable   = triangle_table,
                freq        = freq,
                amp         = amp,
                sample_rate = sample_rate
            ),
            ModulatedVolume(
                ADSREnvelope(
                    attack_duration  = 0.005,
                    decay_duration   = 0.05,
                    sustain_level    = 0.0,
                    release_duration = 0.1,
                    sample_rate      = sample_rate
                )
            )
        )
    )

# ————————————————
def osc_saw_brite(freq, amp, sample_rate):
    """
    Saws con ataque medio y sustain completo:
    ataque 20 ms, decay 100 ms, sustain 100 %, release 300 ms,
    para un carácter brillante y sostenido.
    """
    return iter(
        Chain(
            WavetableOscillator(
                wavetable   = sawtooth_table,
                freq        = freq,
                amp         = amp,
                sample_rate = sample_rate
            ),
            ModulatedVolume(
                ADSREnvelope(
                    attack_duration  = 0.02,
                    decay_duration   = 0.1,
                    sustain_level    = 1.0,
                    release_duration = 0.3,
                    sample_rate      = sample_rate
                )
            )
        )
    )