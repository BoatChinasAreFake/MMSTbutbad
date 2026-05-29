import sys
sys.path.append('scratch')
from parse_mod_data_2024 import parse_base_states
import json

state_owners, state_cores, state_claims, state_provinces = parse_base_states()

# Find all states owned by RAJ or IND in base game
raj_states = [sid for sid, owner in state_owners.items() if owner in ['RAJ', 'IND']]
print("RAJ states count:", len(raj_states))

meta = json.load(open('provinces_meta.json'))
raj_provinces = []
for sid in raj_states:
    for pid in state_provinces.get(sid, []):
        if str(pid) in meta['centers']:
            raj_provinces.append((pid, meta['centers'][str(pid)]))

print("RAJ provinces count:", len(raj_provinces))
if raj_provinces:
    xs = [p[1]['x'] for p in raj_provinces]
    ys = [p[1]['y'] for p in raj_provinces]
    print(f"RAJ/IND geographic bounding box:")
    print(f"  X: {min(xs):.1f} to {max(xs):.1f}, avg: {sum(xs)/len(xs):.1f}")
    print(f"  Y: {min(ys):.1f} to {max(ys):.1f}, avg: {sum(ys)/len(ys):.1f}")
