import numpy as np
from PIL import Image

for name, path in [
    ("rydtguyhuji.jpg", r"C:\Users\Faaz\Downloads\rydtguyhuji.jpg"),
    ("hoi4_map_FRA_2024_01_01_12_1.png", r"C:\Users\Faaz\Downloads\hoi4_map_FRA_2024_01_01_12_1.png")
]:
    try:
        img = Image.open(path)
        print(f"File: {name}")
        print(f"  Size: {img.size}")
        print(f"  Mode: {img.mode}")
        arr = np.array(img.convert('RGB'))
        # Print some pixels around center
        h, w, _ = arr.shape
        print(f"  Center pixel color: {arr[h//2, w//2]}")
    except Exception as e:
        print(f"Error {name}: {e}")
