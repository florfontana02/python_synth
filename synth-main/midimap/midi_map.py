import mido
import time

# 1) Abre tu puerto (ajusta el nombre si hace falta)
inport = mido.open_input("Launchkey Mini MK4 37 MIDI 0")

print("Gira un knob o pulsa un pad… (Ctrl+C para salir)")

try:
    while True:
        msg = inport.receive(block=False)
        if msg and msg.type == 'control_change':
            print(f"CC#{msg.control} → valor {msg.value}")
        time.sleep(0.01)
except KeyboardInterrupt:
    print("¡Listo! Apunta esos números de CC para cada control.")
