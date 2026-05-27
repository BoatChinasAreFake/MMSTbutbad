import json
from PIL import Image
import os

with open("provinces_meta.json", "r") as f:
    meta = json.load(f)

# Find first 20 FRA province coordinates
# We can find them from our list: [3838, 19584, 19586, 19589, 19588, 20609, 3629, 20791, 20790, 6613]
fra_provs = [3838, 19584, 19586, 19589, 19588, 20609, 3629, 20791, 20790, 6613, 20789, 20788, 20787, 11875, 3749, 760, 20792, 6962, 20793, 11720]

un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

for pid in fra_provs:
    center = meta["centers"].get(str(pid))
    if center:
        # In meta, y is bottom-up. Convert to top-down for PIL
        x = center["x"]
        y_meta = center["y"]
        y_pil = 2560 - 1 - y_meta
        color = un_img.getpixel((x, y_pil))
        print(f"Province {pid:5d}: center=({x:4d}, {y_meta:4d}) -> PIL=({x:4d}, {y_pil:4d}) -> UN Color={color}")
