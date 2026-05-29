import os
from PIL import Image

artifacts_dir = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf"
files = os.listdir(artifacts_dir)
print("Artifact images:")
for f in files:
    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        path = os.path.join(artifacts_dir, f)
        try:
            with Image.open(path) as img:
                print(f"  {f}: size {img.size}, mode {img.mode}, {os.path.getsize(path)/1024:.1f} KB")
        except Exception:
            pass

# Also check subdirectories like .tempmediaStorage
temp_dir = os.path.join(artifacts_dir, ".tempmediaStorage")
if os.path.exists(temp_dir):
    print("Temp media storage images:")
    for f in os.listdir(temp_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            path = os.path.join(temp_dir, f)
            try:
                with Image.open(path) as img:
                    print(f"  {f}: size {img.size}, mode {img.mode}, {os.path.getsize(path)/1024:.1f} KB")
            except Exception:
                pass
