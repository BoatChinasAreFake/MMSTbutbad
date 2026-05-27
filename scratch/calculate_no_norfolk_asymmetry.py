import math
from PIL import Image

def run_simulation():
    img = Image.open('provinces.png')
    width, height = img.size
    pixels = img.convert('RGBA').load()

    province_map = [0] * (width * height)
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
            province_map[y * width + x] = id
            if id not in province_centers:
                province_centers[id] = {"sumX": 0, "sumY": 0, "count": 0}
            province_centers[id]["sumX"] += x
            province_centers[id]["sumY"] += y
            province_centers[id]["count"] += 1

    for id in province_centers:
        p = province_centers[id]
        p["x"] = round(p["sumX"] / p["count"])
        p["y"] = round(p["sumY"] / p["count"])

    neighbors = {}
    for y in range(height):
        for x in range(width):
            a = province_map[y * width + x]
            if a not in neighbors: neighbors[a] = set()
            if x + 1 < width:
                b = province_map[y * width + (x + 1)]
                if a != b:
                    neighbors[a].add(b)
                    if b not in neighbors: neighbors[b] = set()
                    neighbors[b].add(a)
            if y + 1 < height:
                b = province_map[(y + 1) * width + x]
                if a != b:
                    neighbors[a].add(b)
                    if b not in neighbors: neighbors[b] = set()
                    neighbors[b].add(a)

    land_set = set(id for id, p in province_centers.items() if p["count"] < 1000)

    gb_all = []
    cornwall_id = province_map[93 * width + 92]
    visited = set()
    queue = [cornwall_id]
    visited.add(cornwall_id)
    while queue:
        curr = queue.pop(0)
        gb_all.append(curr)
        for n in neighbors.get(curr, []):
            if n in land_set and n not in visited:
                n_center = province_centers[n]
                if n_center["x"] > 75:
                    visited.add(n)
                    queue.append(n)

    scotland = [id for id in gb_all if province_centers[id]["y"] < 45]
    wales = [id for id in gb_all if province_centers[id]["x"] < 123 and 45 <= province_centers[id]["y"] <= 80]
    norfolk = [id for id in gb_all if province_centers[id]["x"] > 165 and 55 <= province_centers[id]["y"] <= 75]
    
    england_wales_no_norfolk = [id for id in gb_all if id not in scotland and id not in norfolk]

    def test_optimal_asymmetry(comp, name):
        comp_set = set(comp)
        if len(comp) < 2: return

        # Find optimal straight line
        def is_inside(x, y):
            ix, iy = math.floor(x), math.floor(y)
            if ix < 0 or iy < 0 or ix >= width or iy >= height: return False
            return province_map[iy * width + ix] in comp_set

        best_score = -float('inf')
        A = comp[0]
        B = comp[0]
        for i in range(len(comp)):
            for j in range(i + 1, len(comp)):
                idA = comp[i]
                idB = comp[j]
                pA = province_centers[idA]
                pB = province_centers[idB]
                dist = math.hypot(pB["x"] - pA["x"], pB["y"] - pA["y"])
                
                outside = 0
                for k in range(1, 6):
                    t = k / 6
                    sx = pA["x"] * (1-t) + pB["x"] * t
                    sy = pA["y"] * (1-t) + pB["y"] * t
                    if not is_inside(sx, sy):
                        outside += 1
                
                score = dist - 30 * outside
                if score > best_score:
                    best_score = score
                    A = idA
                    B = idB

        pA = province_centers[A]
        pB = province_centers[B]

        # Line equation from A to B: Ax + By + C = 0
        A_line = pB["y"] - pA["y"]
        B_line = -(pB["x"] - pA["x"])
        C_line = pB["x"]*pA["y"] - pB["y"]*pA["x"]
        denom = math.hypot(A_line, B_line)

        left_area = 0
        right_area = 0
        for id in comp:
            p = province_centers[id]
            val = A_line*p["x"] + B_line*p["y"] + C_line
            if val > 0:
                left_area += p["count"]
            else:
                right_area += p["count"]

        total_area = left_area + right_area
        diff = abs(left_area - right_area)
        asym = diff / total_area if total_area > 0 else 0

        print(f"{name}:")
        print(f"  Optimal straight endpoints: {A} -> {B} (dist = {denom:.2f})")
        print(f"  Left Area: {left_area}")
        print(f"  Right Area: {right_area}")
        print(f"  Asymmetry Ratio: {asym:.4f}")

    test_optimal_asymmetry(england_wales_no_norfolk, "England + Wales (excluding Scotland, no Norfolk)")

run_simulation()
