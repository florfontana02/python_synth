import time
import numpy as np
import mido
import pyaudio
from math import pi, sin
from itertools import count
from synth.components.envelopes import ADSREnvelope
from synth.components.oscillators.oscillators import SineOscillator, SawtoothOscillator, SquareOscillator,TriangleOscillator

# 1) Abrir MIDI
port_name = "Launchkey Mini MK4 37 MIDI 0"
inport = mido.open_input(port_name)

# 2) Configurar audio
SR = 44100
p = pyaudio.PyAudio()
stream = p.open(rate=SR, channels=1, format=pyaudio.paInt16,
                output=True, frames_per_buffer=256,
                output_device_index=4)  # ajustá tu índice

# 3) Diccionario de voces activas
voices = {}

def midi_to_freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

print("Arrancando main.py — Ctrl+C para salir")
try:
    while True:
        # A) Leer MIDI y actualizar voces
        for msg in inport.iter_pending():
            if msg.type == 'note_on' and msg.velocity > 0:
                freq = midi_to_freq(msg.note)
                osc = iter(SquareOscillator(freq=freq, sample_rate=SR))
                env = iter(ADSREnvelope(0.01, 0.1, 0.7, 0.3, sample_rate=SR))
                voices[msg.note] = {'osc': osc, 'env': env}
            elif msg.type in ('note_off',) or (msg.type=='note_on' and msg.velocity==0):
                voices.pop(msg.note, None)

        # B) Generar un bloque de audio
        buf = np.zeros(256, dtype=np.int16)
        for pair in list(voices.values()):
            osc, env = pair['osc'], pair['env']
            samples = np.fromiter((next(osc)*next(env) for _ in range(256)), float)
            buf += (samples * 32767).astype(np.int16)
        stream.write(buf.tobytes())

except KeyboardInterrupt:
    print("Deteniendo…")
    stream.close()
    p.terminate()
