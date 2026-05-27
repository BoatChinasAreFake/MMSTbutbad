import json
import numpy as np
from PIL import Image
from collections import Counter
from parse_mod_data_2024 import parse_base_states

state_owners, state_cores, state_claims, state_provinces = parse_base_states()

# Pre-build province-to-owner lookup
prov_to_owner = {}
for sid, owner in state_owners.items():
    for pid in state_provinces.get(sid, []):
        prov_to_owner[pid] = owner

# Load images
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
    pid_to_color[int(pid)] = tuple(avg_colors[i_item])

# Exclude water
with open("provinces_meta.json", "r") as f:
    meta = json.load(f)
water_provs = set()
for pid_str, center_data in meta.get("centers", {}).items():
    if center_data.get("is_water") or center_data.get("is_lake"):
        water_provs.add(int(pid_str))

# Group base owners by their color in the UN map
color_to_tags = {}
for pid, color in pid_to_color.items():
    if pid in water_provs or pid == 0:
        continue
    owner = prov_to_owner.get(pid)
    if owner is None:
        continue
    
    if color == (61, 83, 114): # Skip ocean background
        continue
        
    if color not in color_to_tags:
        color_to_tags[color] = []
    color_to_tags[color].append(owner)

# Map each unique color to the majority base owner tag
color_to_best_tag = {}
for color, tags_list in color_to_tags.items():
    counts = Counter(tags_list)
    best_tag, count = counts.most_common(1)[0]
    color_to_best_tag[color] = best_tag

print(f"Generated {len(color_to_best_tag)} color-to-tag mappings:")
# France: (72, 131, 150), Russia: (0, 127, 13), China: (178, 34, 59), USA: (53, 104, 165), Australia: (73, 186, 126)
for c in [(72, 131, 150), (0, 127, 13), (178, 34, 59), (53, 104, 165), (73, 186, 126)]:
    print(f"  Color {c} -> Tag: {color_to_best_tag.get(c)}")
