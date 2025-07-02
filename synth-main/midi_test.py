# ejemplo que obtuviste corriendo el debug
CC_MAP = {
    1: 'mod_wheel',
    21: 'master_volume',
    22: 'filter_cutoff',
    23: 'adsr_attack',
    24: 'adsr_decay',
    25: 'adsr_sustain',
    26: 'adsr_release',
    27: 'wavetable_mix'
    # tengo hasta el 38
}

class SynthParams:
    def __init__(self):
        self.master_volume  = 1.0
        self.filter_cutoff  = 5000.0
        self.adsr_attack    = 0.01
        self.adsr_decay     = 0.1
        self.adsr_sustain   = 0.8
        self.adsr_release   = 0.3
        self.wavetable_mix  = 0.0
        # …cualquier otro parámetro…




# en tu main.py…
params = SynthParams()

# …en el método play(), justo al leer mensajes MIDI pendientes…
for msg in self.inport.iter_pending():
    if msg.type == 'control_change':
        attr = CC_MAP.get(msg.control)
        if attr:
            norm = msg.value / 127.0
            # adaptamos cada parámetro a un rango razonable:
            if attr == 'master_volume':
                params.master_volume = norm
            elif attr == 'filter_cutoff':
                # p.e. 200Hz – 10kHz
                params.filter_cutoff = 200 + norm * (10000-200)
            elif attr == 'adsr_attack':
                params.adsr_attack = norm * 0.2        # 0–200ms
            elif attr == 'adsr_decay':
                params.adsr_decay  = norm * 0.5        # 0–500ms
            elif attr == 'adsr_sustain':
                params.adsr_sustain = norm              # 0–1
            elif attr == 'adsr_release':
                params.adsr_release = norm * 1.0       # 0–1s
            elif attr == 'wavetable_mix':
                params.wavetable_mix = norm            # 0–1

            print(f"▶ Par {attr} → {getattr(params, attr):.3f}")
    # luego tu lógica note_on/note_off…
