import json
from parse_mod_data_2024 import parse_colors, parse_valid_tags
from PIL import Image
import numpy as np

# Load database colors
colors = parse_colors()
print("CHI color in DB:", colors.get("CHI"))
print("MOR color in DB:", colors.get("MOR"))
print("CZE color in DB:", colors.get("CZE"))
print("AST color in DB:", colors.get("AST"))

# Let's inspect the downloaded map's color at a known province of China
# E.g. Beijing's province ID. Let's find a province owned by CHI in the 2024 preset
# We can load provinces_index.png and provinces_meta.json to find a coordinate for a Chinese province.
with open("provinces_meta.json", "r") as f:
    meta = json.load(f)

# Find some provinces in China (capital is Beijing, state 629? Let's check state names in localization or just find a province with name Beijing)
# Actually, let's find the average color of all pixels mapped to CHI in the image
idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

idx_arr = np.array(idx_img)
un_arr = np.array(un_img)

prov_ids = idx_arr[:, :, 0].astype(np.uint32) + idx_arr[:, :, 1].astype(np.uint32) * 256 + idx_arr[:, :, 2].astype(np.uint32) * 65536

# Let's find what colors are at pixels for a known China state, e.g. state 1380
# Or let's see: what color is most common in the area of China (e.g. x: 3800, y: 1000)?
# Note: HOI4 coordinates are bottom-up, PIL is top-down. 
# China is in the eastern hemisphere and northern hemisphere, so x around 3800, y around 800 (out of 2560) in top-down coordinates.
# Let's sample a grid in China: x from 3800 to 4000, y from 800 to 1000
sampled_colors = un_arr[800:1000, 3800:4000].reshape(-1, 3)
from collections import Counter
counts = Counter(tuple(c) for c in sampled_colors)
print("Most common colors in China region of the UN map:")
for color, count in counts.most_common(5):
    print(f"  {color}: {count} pixels")
