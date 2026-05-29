import json
import numpy as np
from PIL import Image
import sys
sys.path.append("scratch")
from parse_map_image import parse_colors

colors = parse_colors()
meta = json.load(open("provinces_meta.json"))
idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")
idx_arr = np.array(idx_img, dtype=np.uint32)
un_arr = np.array(un_img, dtype=np.uint8)
prov_ids = idx_arr[:, :, 0] + idx_arr[:, :, 1] * 256 + idx_arr[:, :, 2] * 65536

p = json.load(open("preset_ownership.json"))

cities = [
    ("Beijing", (3720, 930)),
    ("Nanjing", (3780, 1025)),
    ("Shanghai", (3830, 1035))
]

for name, (px, py) in cities:
    pid = int(prov_ids[py, px])
    c = meta["centers"].get(str(pid))
    mask = (prov_ids == pid)
    avg_color = np.mean(un_arr[mask], axis=0)
    owner = p["ownership"].get(str(pid))
    print(f"{name}: PID={pid}, coords=({c['x']}, {c['y']}), avg_color={avg_color}, owner={owner}")
