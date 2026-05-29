import json
import numpy as np
from PIL import Image

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

meta = json.load(open('provinces_meta.json'))
d = json.load(open('preset_ownership.json'))

print("Sample provinces in Germany box:")
count = 0
for pid_str, c in meta['centers'].items():
    if not c.get('is_water') and 2750 < c['x'] < 2900 and 650 < c['y'] < 800:
        pid = int(pid_str)
        mask = (prov_ids == pid)
        if mask.any():
            avg_col = list(un_arr[mask][0])
            owner = d['ownership'].get(pid_str, 'NONE')
            print(f"  PID {pid_str}: coord=({c['x']}, {c['y']}), avg_col={avg_col}, owner={owner}")
            count += 1
            if count >= 15:
                break
