import sys
sys.path.append('scratch')
from parse_mod_data_2024 import parse_base_states
import json

state_owners, state_cores, state_claims, state_provinces = parse_base_states()

# Find all states owned by CHI or PRC in base game
chi_states = [sid for sid, owner in state_owners.items() if owner in ['CHI', 'PRC', 'GXC', 'YUN', 'SHX', 'XSM', 'SIK']]
print("China states count:", len(chi_states))

meta = json.load(open('provinces_meta.json'))
chi_provinces = []
for sid in chi_states:
    for pid in state_provinces.get(sid, []):
        if str(pid) in meta['centers']:
            chi_provinces.append((pid, meta['centers'][str(pid)]))

print("China provinces count:", len(chi_provinces))
if chi_provinces:
    xs = [p[1]['x'] for p in chi_provinces]
    ys = [p[1]['y'] for p in chi_provinces]
    print(f"China geographic bounding box:")
    print(f"  X: {min(xs):.1f} to {max(xs):.1f}, avg: {sum(xs)/len(xs):.1f}")
    print(f"  Y: {min(ys):.1f} to {max(ys):.1f}, avg: {sum(ys)/len(ys):.1f}")
