import json
import numpy as np
from PIL import Image

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

d = json.load(open('preset_ownership.json'))
owners = {}
for pid_str, tag in d['ownership'].items():
    pid = int(pid_str)
    mask = (prov_ids == pid)
    if mask.any():
        avg_col = un_arr[mask][0]
        if np.linalg.norm(avg_col - [115, 100, 90]) < 1.0:
            owners[tag] = owners.get(tag, 0) + 1

print("Owners of [115, 100, 90] color:")
for tag, count in sorted(owners.items(), key=lambda x: x[1], reverse=True):
    print(f"  {tag}: {count} provinces")
