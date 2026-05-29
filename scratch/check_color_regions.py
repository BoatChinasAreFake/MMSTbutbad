import json
import numpy as np
from PIL import Image

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

meta = json.load(open('provinces_meta.json'))

target_colors = {
    (204, 95, 27): "CHI/IND",
    (206, 17, 38): "Red (SHX/PRC/MLW?)",
    (120, 219, 240): "Teal/Blue (GXC/XSM?)",
    (74, 114, 185): "Dark Blue (QAT?)",
    (61, 83, 114): "Greyish Blue (PAK/CHI?)",
    (165, 120, 36): "Brownish Yellow (SAU/YUN?)",
    (230, 100, 0): "Orange (VIN/YUN?)",
    (82, 123, 180): "Blue (LAO/XSM?)",
    (0, 98, 51): "Dark Green (SIK/IRQ?)"
}

for color, label in target_colors.items():
    pids = []
    coords = []
    for pid_str, c in meta['centers'].items():
        pid = int(pid_str)
        if not c.get('is_water') and 3000 < c['x'] < 4500 and 700 < c['y'] < 1400:
            mask = (prov_ids == pid)
            if mask.any():
                avg_col = un_arr[mask][0]
                if np.linalg.norm(avg_col - color) < 15:
                    pids.append(pid)
                    coords.append((c['x'], c['y']))
    if coords:
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        print(f"Color {color} ({label}): {len(pids)} provinces, centroid: ({np.mean(xs):.1f}, {np.mean(ys):.1f})")
