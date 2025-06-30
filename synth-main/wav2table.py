import os
import numpy as np
from scipy.io import wavfile

# 1) Ajusta aquí tu carpeta de samples
samples_dir = r"C:\Users\florc\Desktop\synth-main\synth-main\samples"

# 2) Carpeta de salida para las wavetables
output_dir = r"C:\Users\florc\Desktop\synth-main\synth-main\wavetables"
os.makedirs(output_dir, exist_ok=True)

# 3) Recorre todos los WAVs en samples_dir
for fname in os.listdir(samples_dir):
    if not fname.lower().endswith(".wav"):
        continue

    sample_id = os.path.splitext(fname)[0]
    wav_path  = os.path.join(samples_dir, fname)

    # 4) Carga el WAV
    sr, data = wavfile.read(wav_path)

    # 5) Si es estéreo, conviértelo a mono (promedio de canales)
    if data.ndim > 1:
        data = data.mean(axis=1)

    # 6) Normaliza a [-1,1]
    data = data.astype(float)
    if data.dtype != float:
        # si era int16
        data /= np.iinfo(data.dtype).max
    else:
        data /= np.max(np.abs(data))

    # 7) Guarda la tabla
    out_path = os.path.join(output_dir, f"{sample_id}.npy")
    np.save(out_path, data)
    print(f"Guardada tabla {sample_id}.npy (longitud {len(data)} muestras)")

print("¡Listo! Revisa la carpeta 'wavetables' para tus .npy.")
