import os
from PIL import Image

downloads_path = r"C:\Users\Faaz\Downloads\heightmap(1).bmp"
target_path = "heightmap.png"

if os.path.exists(downloads_path):
    print(f"Found source file at {downloads_path}")
    try:
        img = Image.open(downloads_path)
        img.save(target_path, "PNG")
        print(f"Successfully converted and saved to {target_path}")
    except Exception as e:
        print(f"Error during conversion: {e}")
else:
    print(f"Source file not found at {downloads_path}")
    # Let's list download folder files matching heightmap
    dl_dir = r"C:\Users\Faaz\Downloads"
    if os.path.exists(dl_dir):
        matches = [f for f in os.listdir(dl_dir) if "heightmap" in f.lower()]
        print(f"Found similar files in Downloads: {matches}")
