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

    # Ireland
    visited_ire = set()
    queue_ire = [province_map[50 * width + 40]]
    visited_ire.add(queue_ire[0])
    ireland = []
    while queue_ire:
        curr = queue_ire.pop(0)
        ireland.append(curr)
        for n in neighbors.get(curr, []):
            if n in land_set and n not in visited_ire:
                n_center = province_centers[n]
                if n_center["x"] <= 75:
                    visited_ire.add(n)
                    queue_ire.append(n)

    scotland = [id for id in gb_all if province_centers[id]["y"] < 45]
    wales = [id for id in gb_all if province_centers[id]["x"] < 123 and 45 <= province_centers[id]["y"] <= 80]
    england = [id for id in gb_all if id not in scotland and id not in wales]
    england_wales = [id for id in gb_all if id not in scotland]

    def test_lateral(comp, name):
        comp_set = set(comp)
        if len(comp) < 2: return

        # Geodesic extremities
        def get_furthest(start_id):
            dist = {id: float('inf') for id in comp}
            dist[start_id] = 0
            pq = [(0, start_id)]
            while pq:
                pq.sort(key=lambda x: x[0])
                curr_cost, curr = pq.pop(0)
                if curr_cost > dist[curr]: continue
                curr_center = province_centers[curr]
                for n in neighbors[curr]:
                    if n not in comp_set: continue
                    n_center = province_centers[n]
                    step_dist = math.hypot(curr_center["x"] - n_center["x"], curr_center["y"] - n_center["y"])
                    next_cost = curr_cost + step_dist
                    if next_cost < dist[n]:
                        dist[n] = next_cost
                        pq.append((next_cost, n))
            
            best_id = start_id
            max_d = -1
            for id in comp:
                if dist[id] != float('inf') and dist[id] > max_d:
                    max_d = dist[id]
                    best_id = id
            return best_id, max_d

        A, _ = get_furthest(comp[0])
        B, _ = get_furthest(A)

        pA = province_centers[A]
        pB = province_centers[B]

        # Straight line equation from A to B: Ax + By + C = 0
        A_line = pB["y"] - pA["y"]
        B_line = -(pB["x"] - pA["x"])
        C_line = pB["x"]*pA["y"] - pB["y"]*pA["x"]
        denom = math.hypot(A_line, B_line)

        max_dist = 0
        furthest_prov = A
        for id in comp:
            p = province_centers[id]
            dist = abs(A_line*p["x"] + B_line*p["y"] + C_line) / denom if denom > 0 else 0
            if dist > max_dist:
                max_dist = dist
                furthest_prov = id

        ratio = max_dist / denom if denom > 0 else 0
        print(f"{name}:")
        print(f"  Main axis length (AB): {denom:.2f}")
        print(f"  Max lateral distance: {max_dist:.2f} (province ID {furthest_prov})")
        print(f"  Bulge Ratio (max_lateral / AB): {ratio:.4f}")

    test_lateral(gb_all, "Great Britain Connected")
    test_lateral(england_wales, "England + Wales (excluding Scotland)")
    test_lateral(england, "England Alone (excluding Scotland & Wales)")
    test_lateral(ireland, "Ireland")

run_simulation()
