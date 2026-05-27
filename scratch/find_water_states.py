import os
import re
import json

# Load provinces meta to check which provinces are water
with open('provinces_meta.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)

water_provs = set()
for pid_str, center_data in meta['centers'].items():
    if center_data.get('is_water') or center_data.get('is_lake'):
        water_provs.add(int(pid_str))

states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
files = [f for f in os.listdir(states_dir) if f.endswith('.txt')]

water_in_states = {}
for fname in files:
    fpath = os.path.join(states_dir, fname)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    id_match = re.search(r'id\s*=\s*(\d+)', content)
    if not id_match:
        continue
    sid = int(id_match.group(1))
    
    prov_match = re.search(r'provinces\s*=\s*\{([^}]+)\}', content, re.DOTALL | re.IGNORECASE)
    if prov_match:
        prov_text = prov_match.group(1)
        prov_ids = [int(p) for p in re.findall(r'\b\d+\b', prov_text)]
        prov_water = [p for p in prov_ids if p in water_provs]
        if prov_water:
            water_in_states[sid] = (fname, prov_water)

print(f"Found {len(water_in_states)} states containing water provinces:")
for sid, (fname, pids) in list(water_in_states.items())[:20]:
    print(f"  State {sid} ({fname}): contains {len(pids)} water provinces (e.g. {pids[:5]})")
