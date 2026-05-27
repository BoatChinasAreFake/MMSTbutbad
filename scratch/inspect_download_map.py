from PIL import Image
import os

path = r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png"
print("Exists:", os.path.exists(path))
if os.path.exists(path):
    img = Image.open(path)
    print("Dimensions:", img.size)
