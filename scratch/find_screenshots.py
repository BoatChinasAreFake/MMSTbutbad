import os

downloads = r'C:\Users\Faaz\Downloads'
files = os.listdir(downloads)
screenshot_files = [f for f in files if 'screenshot' in f.lower() or 'image' in f.lower() or 'whatsapp' in f.lower()]
print("Matching files in downloads:")
for f in screenshot_files[:30]:
    path = os.path.join(downloads, f)
    print(f"  {f}: {os.path.getsize(path)/1024:.1f} KB")
