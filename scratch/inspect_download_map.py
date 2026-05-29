import numpy as np
from PIL import Image

path = r"C:\Users\Faaz\Downloads\hoi4_map_FRA_2024_01_01_12_1.png"
img = Image.open(path)
print("Image Mode:", img.mode)
print("Image Size:", img.size)

# Unique colors
arr = np.array(img.convert('RGB'))
flat = arr.reshape(-1, 3)
unique_colors = np.unique(flat, axis=0)
print("Number of unique colors:", len(unique_colors))
print("First 20 unique colors:")
for c in unique_colors[:20]:
    print("  ", list(c))
