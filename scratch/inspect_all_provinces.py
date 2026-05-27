from PIL import Image
import math

img = Image.open('provinces.png')
width, height = img.size
pixels = img.convert('RGBA').load()

province_lookup = {}
province_centers = {}
next_id = 1

for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        key = (r << 24) | (g << 16) | (b << 8) | a
        key = key & 0xffffffff
        if key not in province_lookup:
            province_lookup[key] = next_id
            next_id += 1
        id = province_lookup[key]
        if id not in province_centers:
            province_centers[id] = {"sumX": 0, "sumY": 0, "count": 0, "color": (r, g, b, a)}
        province_centers[id]["sumX"] += x
        province_centers[id]["sumY"] += y
        province_centers[id]["count"] += 1

print(f"Total provinces found: {len(province_centers)}")
# Print them sorted by ID
for id in sorted(province_centers.keys()):
    p = province_centers[id]
    cx = round(p["sumX"] / p["count"])
    cy = round(p["sumY"] / p["count"])
    print(f"ID={id:3d}: Center=({cx:3d}, {cy:3d}), Size={p['count']:5d}, Color={p['color']}")
