import json
import numpy as np
from PIL import Image

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

flat_ids = prov_ids.reshape(-1)
flat_colors = un_arr.reshape(-1, 3)

unique_ids, indices = np.unique(flat_ids, return_inverse=True)
sums = np.zeros((len(unique_ids), 3), dtype=np.uint64)
counts = np.zeros(len(unique_ids), dtype=np.uint64)
np.add.at(sums, indices, flat_colors)
np.add.at(counts, indices, 1)
avg_colors_direct = (sums / counts[:, np.newaxis]).astype(np.uint8)

# Now check with vertical flip
flat_colors_flipped = np.flipud(un_arr).reshape(-1, 3)
sums_flipped = np.zeros((len(unique_ids), 3), dtype=np.uint64)
np.add.at(sums_flipped, indices, flat_colors_flipped)
avg_colors_flipped = (sums_flipped / counts[:, np.newaxis]).astype(np.uint8)

target_color = np.array([24, 61, 64], dtype=np.float32)

print("Checking matching provinces for color [24, 61, 64] (hex 183D40):")

direct_matches = []
for idx_item, pid in enumerate(unique_ids):
    pid = int(pid)
    if pid == 0:
        continue
    if np.linalg.norm(avg_colors_direct[idx_item].astype(np.float32) - target_color) < 15.0:
        direct_matches.append((pid, avg_colors_direct[idx_item]))

flipped_matches = []
for idx_item, pid in enumerate(unique_ids):
    pid = int(pid)
    if pid == 0:
        continue
    if np.linalg.norm(avg_colors_flipped[idx_item].astype(np.float32) - target_color) < 15.0:
        flipped_matches.append((pid, avg_colors_flipped[idx_item]))

print(f"Direct mapping: found {len(direct_matches)} matching provinces.")
print(f"Flipped mapping: found {len(flipped_matches)} matching provinces.")

# Let's inspect some matching province IDs
if direct_matches:
    print("Some Direct matching pids:", [m[0] for m in direct_matches[:20]])
if flipped_matches:
    print("Some Flipped matching pids:", [m[0] for m in flipped_matches[:20]])
