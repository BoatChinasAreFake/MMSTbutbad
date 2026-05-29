import os
from PIL import Image

downloads = r'C:\Users\Faaz\Downloads'
files = [f for f in os.listdir(downloads) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
large_files = []
for f in files:
    path = os.path.join(downloads, f)
    size = os.path.getsize(path)
    if size > 1024 * 1024:
        try:
            with Image.open(path) as img:
                w, h = img.size
            large_files.append((f, size, w, h))
        except Exception:
            pass

print("Large images in downloads:")
for name, sz, w, h in sorted(large_files, key=lambda x: x[1], reverse=True)[:15]:
    print(f"  {name}: {sz/1024/1024:.2f} MB, {w}x{h}")
