import os
import numpy as np
from scipy.io import wavfile
from math import floor

# --- CONFIGURACIÓN ---
# Carpeta con tus .wav
SAMPLES_DIR = r"C:\Users\florc\Desktop\synth-main\synth-main\samples"
# Carpeta donde guardar los wavetables multicycle
OUT_DIR     = r"C:\Users\florc\Desktop\synth-main\synth-main\wavetables_multi"
# Cuántos ciclos quieres extraer de cada sample
K_CYCLES    = 6

os.makedirs(OUT_DIR, exist_ok=True)

# Función para extraer la nota MIDI del nombre de archivo
def midi_from_filename(fname):
    # Asume formato: <instrument>-<note>-<velocity>.wav
    base = os.path.splitext(fname)[0]
    parts = base.split("-")
    return int(parts[-2])

# Convierte nota MIDI a frecuencia
def midi_to_freq(m):
    return 440.0 * (2 ** ((m - 69) / 12.0))

for fname in os.listdir(SAMPLES_DIR):
    if not fname.lower().endswith(".wav"):
        continue

    sample_id = os.path.splitext(fname)[0]
    wav_path  = os.path.join(SAMPLES_DIR, fname)

    # 1) Leer el WAV
    sr, data = wavfile.read(wav_path)
    if data.ndim > 1:
        data = data.mean(axis=1)     # pasar a mono

    data = data.astype(float)
    data /= np.max(np.abs(data))    # normalizar a [-1,1]

    # 2) Determinar nota y período
    midi_note = midi_from_filename(fname)
    freq      = midi_to_freq(midi_note)
    period    = int(sr / freq)      # muestras por ciclo

    # 3) Calcular ventana de K ciclos centrada
    total_len = period * K_CYCLES
    center    = len(data) // 2
    start     = center - total_len//2
    if start < 0:
        start = 0
    end = start + total_len
    if end > len(data):
        # si no hay suficientes muestras al final, recorta y pad con ceros
        fragment = data[start:]
        pad = total_len - len(fragment)
        fragment = np.pad(fragment, (0,pad), 'constant')
    else:
        fragment = data[start:end]

    # 4) Normalizar de nuevo por si acaso
    fragment /= np.max(np.abs(fragment))

    # 5) Guardar como wavetable
    out_path = os.path.join(OUT_DIR, f"{sample_id}_x{K_CYCLES}cycles.npy")
    np.save(out_path, fragment)
    print(f"{sample_id}: freq={freq:.1f}Hz  period={period}  cycles={K_CYCLES} → {fragment.shape[0]} muestras")

print("¡Hecho! Revisa la carpeta 'wavetables_multi'.")
