import json
import numpy as np
from PIL import Image

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

meta = json.load(open('provinces_meta.json'))

# Sample coordinates of countries in 1936
samples = {
    "USA": (1100, 950),
    "CAN": (1000, 600),
    "SOV": (3300, 600),
    "FRA": (2750, 750),
    "GER": (2850, 720),
    "ITA": (2800, 800),
    "JAP": (4100, 1000),
    "CHI": (3700, 1080), # Nationalist China
    "RAJ": (3200, 1200), # British Raj
    "MON": (3600, 880),
}

print("Sampled exact colors from 1936 map:")
for tag, (x, y) in samples.items():
    # Find province at this coordinate
    pixel_idx = y * 5120 + x
    pid = prov_ids.reshape(-1)[pixel_idx]
    if pid > 0:
        mask = (prov_ids == pid)
        if mask.any():
            avg_col = tuple(un_arr[mask][0])
            print(f"  {tag}: {avg_col} (province {pid})")
