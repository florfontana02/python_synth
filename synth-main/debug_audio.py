import pyaudio
import mido

print("Puertos de entrada MIDI disponibles:")
for name in mido.get_input_names():
    print("   ", repr(name))


p = pyaudio.PyAudio()
print("Dispositivos de salida de audio:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxOutputChannels'] > 0:
        print(f"  Índice {i}: {info['name']}")
p.terminate()

