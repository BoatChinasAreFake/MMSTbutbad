import sys
sys.path.append('scratch')
from parse_mod_data_2024 import parse_base_states, parse_2024_transfers
import json

state_owners, state_cores, state_claims, state_provinces = parse_base_states()
current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)

meta = json.load(open('provinces_meta.json'))
prov_coords = {int(pid): (float(c['x']), float(c['y'])) for pid, c in meta['centers'].items() if not c.get('is_water')}

for tag in ['ETH', 'IND', 'RAJ', 'PRC']:
    coords = []
    for sid, owner in current_owners.items():
        if owner == tag:
            for pid in state_provinces.get(sid, []):
                if pid in prov_coords:
                    coords.append(prov_coords[pid])
    if coords:
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        print(f"{tag} calculated centroid: ({sum(xs)/len(xs):.1f}, {sum(ys)/len(ys):.1f})")
    else:
        print(f"{tag} has no 2024 states")
