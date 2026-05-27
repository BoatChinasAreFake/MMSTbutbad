import json
import numpy as np
from PIL import Image
from collections import Counter
from parse_mod_data_2024 import parse_base_states

state_owners, state_cores, state_claims, state_provinces = parse_base_states()

prov_to_owner = {}
for sid, owner in state_owners.items():
    for pid in state_provinces.get(sid, []):
        prov_to_owner[pid] = owner

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

for test_color in [(72, 131, 150), (0, 127, 13), (178, 34, 59), (53, 104, 165), (73, 186, 126)]:
    tags = []
    tc = np.array(test_color, dtype=np.float32)
    for pid, color in pid_to_color.items():
        if pid in water_provs or pid == 0:
            continue
        c = np.array(color, dtype=np.float32)
        if np.linalg.norm(c - tc) < 10.0:
            owner = prov_to_owner.get(pid)
            if owner:
                tags.append(owner)
    
    print(f"\nColor {test_color} counts (with distance < 10.0):")
    cnts = Counter(tags)
    for tag, c in cnts.most_common(10):
        print(f"  {tag}: {c} provinces")
