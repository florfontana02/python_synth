import os
import numpy as np
from scipy.io import wavfile

samples_dir = r"C:\Users\florc\Desktop\synth-main\synth-main\samples"

output_dir = r"C:\Users\florc\Desktop\synth-main\synth-main\wavetables"
os.makedirs(output_dir, exist_ok=True)


for fname in os.listdir(samples_dir):
    if not fname.lower().endswith(".wav"):
        continue

    sample_id = os.path.splitext(fname)[0]
    wav_path  = os.path.join(samples_dir, fname)

    sr, data = wavfile.read(wav_path)

    if data.ndim > 1:
        data = data.mean(axis=1)

    data = data.astype(float)
    if data.dtype != float:
        # si era int16
        data /= np.iinfo(data.dtype).max
    else:
        data /= np.max(np.abs(data))

    out_path = os.path.join(output_dir, f"{sample_id}.npy")
    np.save(out_path, data)
    print(f"Guardada tabla {sample_id}.npy (longitud {len(data)} muestras)")

print("listoooo")



#### one cycle wavetable
import os, numpy as np
from scipy.io import wavfile
from math import floor


SAMPLE_RATE = 44100
samples_dir = r"C:\Users\florc\Desktop\synth-main\synth-main\samples"
out_dir     = r"C:\Users\florc\Desktop\synth-main\wavetables_cycle"
os.makedirs(out_dir, exist_ok=True)

for fn in os.listdir(samples_dir):
    if not fn.lower().endswith(".wav"): continue
    # 1) Extraer nota MIDI del nombre
    name, _     = os.path.splitext(fn)
    parts       = name.split("-")
    note        = int(parts[-2])            # e.g. "049"
    # 2) Calcula frecuencia y periodo
    freq        = 440.0 * 2 ** ((note - 69) / 12.0)
    period      = int(SAMPLE_RATE / freq)
    # 3) Lee el wav y conviértelo a mono
    sr, data    = wavfile.read(os.path.join(samples_dir, fn))
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(float)
    data /= np.max(np.abs(data))
    # 4) Elige el centro para steady‐state
    center      = len(data) // 2
    start       = max(0, center - period//2)
    table       = data[start : start + period]
    # Si no alcanza, pad con ceros
    if len(table) < period:
        pad = period - len(table)
        table = np.pad(table, (0, pad), 'constant')
    # 5) Normaliza de nuevo y guarda
    table /= np.max(np.abs(table))
    np.save(os.path.join(out_dir, f"{name}_cycle.npy"), table)
    print(f"→ {name}: cycle length {period}")
