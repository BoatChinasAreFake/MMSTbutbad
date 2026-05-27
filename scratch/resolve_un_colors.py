import json
import numpy as np
from PIL import Image
import os

# Load database tags and colors
from parse_mod_data_2024 import parse_colors, parse_localisation, parse_valid_tags, parse_base_states, parse_2024_transfers

valid_tags = parse_valid_tags()
names = parse_localisation(valid_tags)
colors = parse_colors()

state_owners, state_cores, state_claims, state_provinces = parse_base_states()
current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)
active_2024_tags = set(current_owners.values())
if 'EUR' in active_2024_tags:
    active_2024_tags.remove('EUR')

# Load provinces meta
with open("provinces_meta.json", "r") as f:
    meta = json.load(f)

water_provs = set()
for pid_str, center_data in meta.get("centers", {}).items():
    if center_data.get("is_water") or center_data.get("is_lake"):
        water_provs.add(int(pid_str))

print("Sampling UN map colors using 2024 post-transfer owners...")
idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

idx_arr = np.array(idx_img, dtype=np.uint32)
un_arr = np.array(un_img, dtype=np.uint8)

prov_ids = idx_arr[:, :, 0] + idx_arr[:, :, 1] * 256 + idx_arr[:, :, 2] * 65536
flat_ids = prov_ids.reshape(-1)
flat_colors = un_arr.reshape(-1, 3)

unique_ids, indices = np.unique(flat_ids, return_inverse=True)

# Build a map from province ID to average color in UN map
sums = np.zeros((len(unique_ids), 3), dtype=np.uint64)
counts = np.zeros(len(unique_ids), dtype=np.uint64)
np.add.at(sums, indices, flat_colors)
np.add.at(counts, indices, 1)
avg_colors = (sums / counts[:, np.newaxis]).astype(np.uint8)

pid_to_color = {}
for i_item, pid in enumerate(unique_ids):
    pid_to_color[int(pid)] = list(avg_colors[i_item])

tag_to_un_colors = {}
for sid, owner in current_owners.items():
    if owner not in active_2024_tags:
        continue
    provs = state_provinces.get(sid, [])
    for pid in provs:
        if pid in water_provs or pid not in pid_to_color:
            continue
        c = tuple(pid_to_color[pid])
        if c == (38, 50, 68): # Skip background
            continue
        if owner not in tag_to_un_colors:
            tag_to_un_colors[owner] = []
        tag_to_un_colors[owner].append(c)

tag_to_resolved_color = {}
from collections import Counter
for tag, colors_list in tag_to_un_colors.items():
    counts = Counter(colors_list)
    majority_color, count = counts.most_common(1)[0]
    # Convert numpy types to standard Python ints for JSON serialization
    tag_to_resolved_color[tag] = [int(x) for x in majority_color]

print(f"Resolved exact UN colors for {len(tag_to_resolved_color)} active tags.")
for tag in ['PRC', 'CHI', 'RUS', 'USA', 'WGR', 'FRA', 'POL', 'AST', 'CAN', 'BRA']:
    print(f"  {tag}: {tag_to_resolved_color.get(tag)}")

with open("scratch/resolved_un_colors.json", "w") as f:
    json.dump(tag_to_resolved_color, f, indent=2)
print("Saved resolved colors to scratch/resolved_un_colors.json")
