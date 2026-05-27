import json
import numpy as np
from PIL import Image

idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

width, height = idx_img.size
print(f"Index size: {width}x{height}")
print(f"UN map size: {un_img.size}")

# Let's find some land provinces in the index map and see where their coordinates match land in the UN map.
# We will sample 10 coordinates that are land in provinces_index.png (not black or water)
# and print their color in the UN map under:
# 1. Direct mapping: (x, y)
# 2. Y-flipped: (x, height - 1 - y)
# 3. X-flipped: (width - 1 - x, y)
# 4. Both flipped: (width - 1 - x, height - 1 - y)

# Let's load the provinces metadata to find land province centers
with open("provinces_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

centers = meta.get("centers", {})
land_coords = []
for pid_str, cdata in centers.items():
    if not cdata.get("is_water") and not cdata.get("is_lake"):
        x, y = int(cdata["x"]), int(cdata["y"])
        # ensure it's within bounds
        if 0 <= x < width and 0 <= y < height:
            land_coords.append((pid_str, x, y))
            if len(land_coords) >= 10:
                break

print("\nSampling 10 land provinces:")
for pid_str, x, y in land_coords:
    idx_col = idx_img.getpixel((x, y))
    direct_col = un_img.getpixel((x, y))
    y_flipped_col = un_img.getpixel((x, height - 1 - y))
    
    print(f"Province {pid_str} at ({x}, {y}):")
    print(f"  Index pixel: {idx_col}")
    print(f"  Direct pixel: {direct_col}")
    print(f"  Y-flipped: {y_flipped_col}")
