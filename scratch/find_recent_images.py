import os
import time

downloads = r'C:\Users\Faaz\Downloads'
files = os.listdir(downloads)
now = time.time()
print("Recently modified images in downloads (last 7 days):")
for f in files:
    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        path = os.path.join(downloads, f)
        mtime = os.path.getmtime(path)
        # modified within last 7 days (7 * 24 * 3600 seconds)
        if now - mtime < 7 * 24 * 3600:
            from PIL import Image
            try:
                with Image.open(path) as img:
                    w, h = img.size
                print(f"  {f}: {os.path.getsize(path)/1024:.1f} KB, size {w}x{h}, mtime {time.ctime(mtime)}")
            except Exception:
                pass
