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

colors = {}
for pid_str, tag in d['ownership'].items():
    if tag == 'PRC' and pid_str in meta['centers'] and 3000 < meta['centers'][pid_str]['x'] < 3500 and 1000 < meta['centers'][pid_str]['y'] < 1400:
        pid = int(pid_str)
        mask = (prov_ids == pid)
        if mask.any():
            col = tuple(un_arr[mask][0])
            colors[col] = colors.get(col, 0) + 1

print("Colors of PRC provinces in India box:")
for col, count in sorted(colors.items(), key=lambda x: x[1], reverse=True):
    print(f"  {col}: {count} provinces")
