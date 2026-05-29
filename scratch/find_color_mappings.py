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

# Let's map each unique color in the 1936 map to the tag that has the most provinces of that color
color_to_provinces = {}
for pid_str, c in meta['centers'].items():
    if not c.get('is_water'):
        pid = int(pid_str)
        mask = (prov_ids == pid)
        if mask.any():
            col = tuple(un_arr[mask][0])
            color_to_provinces.setdefault(col, []).append(pid)

print(f"Found {len(color_to_provinces)} unique colors in the 1936 map.")

# For each color, see which 1936 base state owner owns the most provinces of this color
from collections import Counter
color_to_tag = {}
for col, pids in color_to_provinces.items():
    owners = []
    for pid in pids:
        # Find which state this province belongs to
        for sid, provs in state_provinces.items():
            if pid in provs:
                owners.append(state_owners.get(sid))
                break
    if owners:
        c = Counter(owners)
        top_tag, count = c.most_common(1)[0]
        color_to_tag[col] = (top_tag, count, len(pids))

# Sort colors by number of provinces
sorted_colors = sorted(color_to_tag.items(), key=lambda x: x[1][2], reverse=True)
print("\nColor mapping to tags based on province ownership:")
for col, (tag, count, total) in sorted_colors:
    print(f"  {col} -> {tag} ({count}/{total} provinces)")
