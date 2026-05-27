from PIL import Image
import math

def find_lake():
    img = Image.open('provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

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
            pid = province_lookup[key]
            if pid not in province_centers:
                province_centers[pid] = {
                    "sumX": 0, "sumY": 0, "count": 0, "key": key, "color": (r, g, b, a), "pixels": []
                }
            province_centers[pid]["sumX"] += x
            province_centers[pid]["sumY"] += y
            province_centers[pid]["count"] += 1
            province_centers[pid]["pixels"].append((x, y))

    for pid in province_centers:
        p = province_centers[pid]
        p["x"] = p["sumX"] / p["count"]
        p["y"] = p["sumY"] / p["count"]

    # Water (ocean) province
    sorted_pids = sorted(province_centers.keys(), key=lambda pid: province_centers[pid]["count"], reverse=True)
    water_pid = sorted_pids[0]
    water_key = province_centers[water_pid]["key"]

    print(f"Ocean (Water) province: ID={water_pid}, Key={water_key}, Color={province_centers[water_pid]['color']}")

    # Let's inspect provinces in Ireland (x < 75) that might be lakes.
    # Lough Neagh is a fairly large lake in Northern Ireland.
    # Let's print all provinces in Ireland with their center and color.
    ireland_provinces = []
    for pid, p in province_centers.items():
        if pid != water_pid and p["x"] < 75 and p["count"] > 1:
            ireland_provinces.append((pid, p))
    
    # Sort by size to see the largest ones
    ireland_provinces.sort(key=lambda x: x[1]["count"], reverse=True)
    
    print("\n--- Largest Provinces in Ireland region ---")
    for pid, p in ireland_provinces[:15]:
        print(f"ID={pid:3d}, Key={p['key']:10d}, Color={p['color']}, Center=({p['x']:.1f}, {p['y']:.1f}), Size={p['count']}")

if __name__ == '__main__':
    find_lake()
