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

    # GB connected starting from cornwall
    cornwall_id = province_map[93 * width + 92]
    visited = set()
    queue = [cornwall_id]
    visited.add(cornwall_id)
    gb_all = []
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

    def test_deviation(comp, name):
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
        B, S_geo = get_furthest(A)

        # Get geodesic path
        dist = {id: float('inf') for id in comp}
        prev = {}
        dist[A] = 0
        pq = [(0, A)]
        while pq:
            pq.sort(key=lambda x: x[0])
            curr_cost, curr = pq.pop(0)
            if curr == B: break
            for n in neighbors[curr]:
                if n not in comp_set: continue
                next_cost = curr_cost + 1
                if next_cost < dist[n]:
                    dist[n] = next_cost
                    prev[n] = curr
                    pq.append((next_cost, n))
        path_ids = []
        cur = B
        while cur is not None:
            path_ids.append(cur)
            cur = prev.get(cur)
        path_ids.reverse()

        path = [[province_centers[id]["x"], province_centers[id]["y"]] for id in path_ids]
        P0 = path[0]
        P3 = path[-1]

        # Calculate deviation of each path point from the line P0 -> P3
        # Line equation: (y3 - y0)*x - (x3 - x0)*y + x3*y0 - y3*x0 = 0
        # Perpendicular distance = |Ax + By + C| / sqrt(A^2 + B^2)
        A_line = P3[1] - P0[1]
        B_line = -(P3[0] - P0[0])
        C_line = P3[0]*P0[1] - P3[1]*P0[0]
        denom = math.hypot(A_line, B_line)

        max_dev = 0
        if denom > 0:
            for pt in path:
                dev = abs(A_line*pt[0] + B_line*pt[1] + C_line) / denom
                if dev > max_dev:
                    max_dev = dev

        norm_dev = max_dev / denom if denom > 0 else 0
        print(f"{name}:")
        print(f"  Geodesic distance: {S_geo:.2f}")
        print(f"  Straight distance: {denom:.2f}")
        print(f"  Max deviation: {max_dev:.2f}")
        print(f"  Normalized deviation (dev/straight): {norm_dev:.4f}")

    test_deviation(gb_all, "Great Britain Connected")
    test_deviation(england_wales, "England + Wales (excluding Scotland)")
    test_deviation(england, "England Alone (excluding Scotland & Wales)")
    test_deviation(ireland, "Ireland")

run_simulation()
