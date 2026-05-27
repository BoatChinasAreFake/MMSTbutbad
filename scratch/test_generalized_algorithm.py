import sys
import math
from PIL import Image

def simulate():
    img = Image.open('c:/Users/Faaz/Documents/GitHub/Mappa Mundi sine Tempore/provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

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

    # Helper to flood fill
    def get_component(start_x, start_y, x_filter=None):
        start_id = province_map[start_y * width + start_x]
        visited = set()
        queue = [start_id]
        visited.add(start_id)
        comp = []
        while queue:
            curr = queue.pop(0)
            comp.append(curr)
            for n in neighbors.get(curr, []):
                if n in land_set and n not in visited:
                    n_center = province_centers[n]
                    if x_filter is None or x_filter(n_center["x"]):
                        visited.add(n)
                        queue.append(n)
        return comp

    # Define components
    ireland = get_component(40, 50, lambda x: x <= 75)
    # Great Britain connected (including Scotland)
    gb_all = get_component(93, 92)

    # Standalone England (excluding Scotland - top 12 GB provinces by Y)
    gb_sorted_by_y = sorted(gb_all, key=lambda id: province_centers[id]["y"])
    scotland_ids = set(gb_sorted_by_y[:12])
    england = [id for id in gb_all if id not in scotland_ids]

    def analyze_component(comp, name):
        comp_set = set(comp)
        
        # 1. Geodesic extremities
        # Depth
        depth = {}
        depth_queue = []
        for id in comp:
            is_boundary = False
            curr_neighbors = neighbors.get(id, [])
            if len(curr_neighbors) < 4: is_boundary = True
            for n in curr_neighbors:
                if n not in comp_set:
                    is_boundary = True
                    break
            if is_boundary:
                depth[id] = 1
                depth_queue.append(id)
        if not depth_queue and comp:
            depth[comp[0]] = 1
            depth_queue.append(comp[0])
        while depth_queue:
            curr = depth_queue.pop(0)
            curr_depth = depth[curr]
            for n in neighbors.get(curr, []):
                if n in comp_set and n not in depth:
                    depth[n] = curr_depth + 1
                    depth_queue.append(n)
        max_d = max(depth.values()) if depth else 1

        A_geo = comp[0]
        B_geo = comp[0]
        max_geodesic_dist = -1
        for start_id in comp:
            dist = {id: float('inf') for id in comp}
            dist[start_id] = 0
            pq = [(0, start_id)]
            while pq:
                pq.sort(key=lambda x: x[0])
                curr_cost, curr = pq.pop(0)
                if curr_cost > dist[curr]: continue
                curr_center = province_centers[curr]
                for n in neighbors.get(curr, []):
                    if n not in comp_set: continue
                    n_center = province_centers[n]
                    step_dist = math.hypot(curr_center["x"] - n_center["x"], curr_center["y"] - n_center["y"])
                    next_cost = curr_cost + step_dist
                    if next_cost < dist[n]:
                        dist[n] = next_cost
                        pq.append((next_cost, n))
            for end_id in comp:
                if dist[end_id] != float('inf') and dist[end_id] > max_geodesic_dist:
                    max_geodesic_dist = dist[end_id]
                    A_geo = start_id; B_geo = end_id

        # 2. Optimal straight line search
        def is_inside(x, y):
            ix, iy = math.floor(x), math.floor(y)
            if ix < 0 or iy < 0 or ix >= width or iy >= height: return False
            return province_map[iy * width + ix] in comp_set

        best_straight_score = -float('inf')
        best_straight_len = 0
        for i in range(len(comp)):
            for j in range(i + 1, len(comp)):
                idA = comp[i]
                idB = comp[j]
                pA = province_centers[idA]
                pB = province_centers[idB]
                dist = math.hypot(pB["x"] - pA["x"], pB["y"] - pA["y"])
                
                outside_count = 0
                for k in range(1, 6):
                    t = k / 6
                    sx = pA["x"] * (1 - t) + pB["x"] * t
                    sy = pA["y"] * (1 - t) + pB["y"] * t
                    if not is_inside(sx, sy):
                        outside_count += 1
                
                score = dist - 30 * outside_count
                if score > best_straight_score:
                    best_straight_score = score
                    best_straight_len = dist

        # Straightness ratio
        sr = best_straight_len / max_geodesic_dist if max_geodesic_dist > 0 else 0
        
        print(f"\n[{name}]")
        print(f"  Geodesic Distance (S_geo) = {max_geodesic_dist:.2f}")
        print(f"  Optimal Straight Length   = {best_straight_len:.2f}")
        print(f"  Straightness Ratio (SR)   = {sr:.3f}")

    analyze_component(ireland, "Ireland")
    analyze_component(gb_all, "Great Britain Connected")
    analyze_component(england, "England Standalone")

simulate()
