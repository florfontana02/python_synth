import pyaudio, numpy as np
from math import pi, sin
from pygame import midi
from itertools import count
from synth.components.envelopes import ADSREnvelope

midi.init()
mi = midi.Input(device_id=midi.get_default_input_id())

p = pyaudio.PyAudio()
st = p.open(
    rate=44100, channels=1, format=pyaudio.paInt16,
    output=True, frames_per_buffer=256,
    output_device_index=4
)

nd = {}
NOTE_ON, NOTE_OFF = 0x90, 0x80

try:
    print("🎹 Live synth con ADSR corriendo…")
    while True:
        # — Generación de audio —
        if nd:
            buf = np.zeros(256, dtype=np.int16)
            for note, pair in list(nd.items()):
                osc, env = pair['osc'], pair['env']
                samples = []
                for _ in range(256):
                    amp = next(env)
                    samples.append(int(next(osc) * amp * 32767))
                buf[:len(samples)] += np.array(samples, dtype=np.int16)
                if env.ended:
                    nd.pop(note)
            st.write(buf.tobytes())

        # — Lectura MIDI —
        if mi.poll():
            for (status, note, vel, _), _ in mi.read(16):
                event = status & 0xF0

                # Note On
                if event == NOTE_ON and vel > 0:
                    freq = midi.midi_to_frequency(note)
                    osc = (
                        sin(c) * (vel/127.0)
                        for c in count(0, 2*pi*freq/44100)
                    )
                    env = ADSREnvelope(
                        attack_duration=0.05,
                        decay_duration=0.1,
                        sustain_level=0.8,
                        release_duration=0.3,
                        sample_rate=44100
                    )
                    next(env)
                    nd[note] = {'osc': osc, 'env': env}

                # Note Off
                elif event == NOTE_OFF or (event == NOTE_ON and vel == 0):
                    if note in nd:
                        nd[note]['env'].trigger_release()

except KeyboardInterrupt:
    mi.close()
    st.close()
    p.terminate()
