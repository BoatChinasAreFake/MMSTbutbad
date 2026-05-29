import sys
sys.path.append('scratch')
from parse_mod_data_2024 import parse_base_states
import json
import numpy as np
from PIL import Image

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

meta = json.load(open('provinces_meta.json'))
state_owners, state_cores, state_claims, state_provinces = parse_base_states()

tags_to_check = ["USA", "CAN", "SOV", "FRA", "GER", "ITA", "JAP", "CHI", "RAJ", "MON", "GXC", "YUN", "SHX", "SIK", "TIB", "XSM"]

print("Exact 1936 colors from states mapping:")
for tag in tags_to_check:
    # Find all provinces belonging to this tag in base states
    state_ids = [sid for sid, owner in state_owners.items() if owner == tag]
    pids = []
    for sid in state_ids:
        pids.extend(state_provinces.get(sid, []))
    
    # Get average colors of these provinces in the 1936 map
    colors_found = {}
    for pid in pids:
        if str(pid) in meta['centers'] and not meta['centers'][str(pid)].get('is_water'):
            mask = (prov_ids == pid)
            if mask.any():
                col = tuple(un_arr[mask][0])
                colors_found[col] = colors_found.get(col, 0) + 1
                
    if colors_found:
        # Get the top color
        top_color, count = max(colors_found.items(), key=lambda x: x[1])
        total = sum(colors_found.values())
        print(f"  {tag}: {list(top_color)} (matched {count}/{total} provinces)")
    else:
        print(f"  {tag}: no provinces found")
