import json
from PIL import Image
import os
import numpy as np

with open("provinces_meta.json", "r") as f:
    meta = json.load(f)

# Find some provinces owned by ITA in base states
from parse_mod_data_2024 import parse_base_states
state_owners, state_cores, state_claims, state_provinces = parse_base_states()

ita_provs = []
for sid, owner in state_owners.items():
    if owner == 'ITA':
        ita_provs.extend(state_provinces.get(sid, []))

print("Total base provinces for ITA:", len(ita_provs))

un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

for pid in ita_provs[:10]:
    center = meta["centers"].get(str(pid))
    if center:
        x = center["x"]
        y = center["y"] # Note: we found there is no flip, so PIL y should match center y
        # Let's print both unflipped and flipped just to be absolutely sure!
        print(f"Province {pid:5d}: center=({x:4d}, {y:4d})")
        print(f"  UN Color (unflipped): {un_img.getpixel((x, y))}")
        print(f"  UN Color (flipped):   {un_img.getpixel((x, 2560 - 1 - y))}")
