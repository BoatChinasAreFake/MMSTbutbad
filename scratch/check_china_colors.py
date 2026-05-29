import numpy as np
from PIL import Image
import json

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

meta = json.load(open('provinces_meta.json'))
colors = {}
for pid_str, c in meta['centers'].items():
    pid = int(pid_str)
    if not c.get('is_water') and 3200 < c['x'] < 4200 and 800 < c['y'] < 1200:
        mask = (prov_ids == pid)
        if mask.any():
            col = tuple(un_arr[mask][0])
            colors[col] = colors.get(col, 0) + 1

print("Top colors in China region:")
for col, count in sorted(colors.items(), key=lambda x: x[1], reverse=True)[:25]:
    print(f"  {col}: {count} provinces")
