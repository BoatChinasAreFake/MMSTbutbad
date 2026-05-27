from PIL import Image
import math

def find_closest():
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

    # Calculate centers
    for pid in province_centers:
        p = province_centers[pid]
        p["x"] = p["sumX"] / p["count"]
        p["y"] = p["sumY"] / p["count"]

    # Filter land provinces (exclude water)
    sorted_pids = sorted(province_centers.keys(), key=lambda pid: province_centers[pid]["count"], reverse=True)
    water_pid = sorted_pids[0]
    print(f"Detected water province ID={water_pid}, pixels={province_centers[water_pid]['count']}")

    land_provinces = {pid: p for pid, p in province_centers.items() if pid != water_pid}

    # Group into Ireland and Great Britain based on X coordinate
    ireland = {pid: p for pid, p in land_provinces.items() if p["x"] < 75}
    gb = {pid: p for pid, p in land_provinces.items() if p["x"] >= 75}

    print(f"Ireland has {len(ireland)} provinces.")
    print(f"Great Britain has {len(gb)} provinces.")

    # Find candidate pairs with center distance < 50
    candidates = []
    for pid_ire in ireland:
        p_ire = ireland[pid_ire]
        for pid_gb in gb:
            p_gb = gb[pid_gb]
            center_dist = math.hypot(p_ire["x"] - p_gb["x"], p_ire["y"] - p_gb["y"])
            if center_dist < 50:
                candidates.append((center_dist, pid_ire, p_ire, pid_gb, p_gb))

    print(f"Number of candidate pairs to scan at pixel level: {len(candidates)}")

    results = []
    for center_dist, pid_ire, p_ire, pid_gb, p_gb in candidates:
        px_dist = float('inf')
        closest_pix = None
        # Sub-sample pixels or run the scan
        # Since candidate size is small, we can run it
        for x1, y1 in p_ire["pixels"]:
            for x2, y2 in p_gb["pixels"]:
                d = math.hypot(x1 - x2, y1 - y2)
                if d < px_dist:
                    px_dist = d
                    closest_pix = ((x1, y1), (x2, y2))
        
        results.append((px_dist, pid_ire, p_ire, pid_gb, p_gb, closest_pix))

    results.sort(key=lambda x: x[0])

    if results:
        best = results[0]
        px_dist, pid_ire, p_ire, pid_gb, p_gb, closest_pix = best
        print("\n--- CLOSEST PROVINCE PAIR (STRAIT OPTION) ---")
        print(f"Ireland Province: ID={pid_ire}, Key={p_ire['key']}, Color={p_ire['color']}, Center=({p_ire['x']:.1f}, {p_ire['y']:.1f})")
        print(f"Great Britain Province: ID={pid_gb}, Key={p_gb['key']}, Color={p_gb['color']}, Center=({p_gb['x']:.1f}, {p_gb['y']:.1f})")
        print(f"Minimum Pixel Distance: {px_dist:.2f} pixels")
        print(f"Closest Pixels: {closest_pix[0]} <-> {closest_pix[1]}")

        print("\n--- ALL PAIRS WITHIN 15 PIXELS (OTHER STRAIT OPTIONS) ---")
        for px_dist, pid_ire, p_ire, pid_gb, p_gb, closest_pix in results:
            if px_dist <= 15:
                print(f"Dist={px_dist:5.2f}px: Ire_ID={pid_ire} (Key={p_ire['key']}, Color={p_ire['color']}) <-> GB_ID={pid_gb} (Key={p_gb['key']}, Color={p_gb['color']})")

if __name__ == '__main__':
    find_closest()
