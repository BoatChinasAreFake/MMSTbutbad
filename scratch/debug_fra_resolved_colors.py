import json
import numpy as np
from PIL import Image
from collections import Counter

from parse_mod_data_2024 import parse_base_states, parse_2024_transfers, parse_colors

state_owners, state_cores, state_claims, state_provinces = parse_base_states()
current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)

idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

idx_arr = np.array(idx_img, dtype=np.uint32)
un_arr = np.array(un_img, dtype=np.uint8)

prov_ids = idx_arr[:, :, 0] + idx_arr[:, :, 1] * 256 + idx_arr[:, :, 2] * 65536
flat_ids = prov_ids.reshape(-1)
flat_colors = un_arr.reshape(-1, 3)

unique_ids, indices = np.unique(flat_ids, return_inverse=True)

sums = np.zeros((len(unique_ids), 3), dtype=np.uint64)
counts = np.zeros(len(unique_ids), dtype=np.uint64)
np.add.at(sums, indices, flat_colors)
np.add.at(counts, indices, 1)
avg_colors = (sums / counts[:, np.newaxis]).astype(np.uint8)

pid_to_color = {}
for i_item, pid in enumerate(unique_ids):
    pid_to_color[int(pid)] = list(avg_colors[i_item])

# Exclude water
with open("provinces_meta.json", "r") as f:
    meta = json.load(f)
water_provs = set()
for pid_str, center_data in meta.get("centers", {}).items():
    if center_data.get("is_water") or center_data.get("is_lake"):
        water_provs.add(int(pid_str))

for tag in ['FRA', 'RUS', 'USA']:
    sampled = []
    # Find all states owned by tag
    states = [sid for sid, owner in current_owners.items() if owner == tag]
    for sid in states:
        provs = state_provinces.get(sid, [])
        for pid in provs:
            if pid in water_provs or pid not in pid_to_color:
                continue
            c = tuple(pid_to_color[pid])
            if c == (61, 83, 114): # Skip ocean background color
                continue
            sampled.append(c)
    
    print(f"\n--- Sampled colors for {tag} (total {len(sampled)}): ---")
    counts = Counter(sampled)
    for color, count in counts.most_common(10):
        print(f"  {color}: {count} provinces")
