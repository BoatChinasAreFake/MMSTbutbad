import math
from PIL import Image

def analyze():
    img = Image.open('provinces.png')
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
                if n_center["x"] > 75: # filter out Ireland/isle of man
                    visited.add(n)
                    queue.append(n)

    # Sort GB by y
    gb_sorted_by_y = sorted(gb_all, key=lambda id: province_centers[id]["y"])
    
    # We want to identify the parts of Great Britain
    # Scotland is at the north (small y values)
    # Wales is on the west
    # England is the rest
    
    scotland_ids = set(gb_sorted_by_y[:12]) # Top 12 are scotland
    england_and_wales = [id for id in gb_all if id not in scotland_ids]
    
    # Let's find Wales. Wales center x is typically smaller (to the west, e.g., between 80 and 125, y between 90 and 150)
    # Let's define Wales by coordinates or topology
    wales_ids = set()
    for id in england_and_wales:
        c = province_centers[id]
        # Wales boundary is roughly: x < 125 and y between 95 and 145
        if c["x"] < 122 and 95 <= c["y"] <= 145:
            wales_ids.add(id)
            
    # Cornwall can be identified as x < 105, y > 150
    cornwall_ids = set()
    for id in england_and_wales:
        c = province_centers[id]
        if c["x"] < 105 and c["y"] > 150:
            cornwall_ids.add(id)

    # East Anglia ( Norfolk/Suffolk area)
    # The easternmost province is at the far right of England, roughly x > 175, y between 110 and 140
    east_anglia_ids = set()
    for id in england_and_wales:
        c = province_centers[id]
        if c["x"] > 170 and 110 <= c["y"] <= 140:
            east_anglia_ids.add(id)

    # Let's define England alone as england_and_wales without Wales
    england_alone = [id for id in england_and_wales if id not in wales_ids]

    def compute_extremities(comp):
        comp_set = set(comp)
        if not comp: return 0, 0, 1
        
        # 2-pass Dijkstra
        def get_furthest(start_id):
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
            
            furthest_id = start_id
            max_d = -1
            for id in comp:
                if dist[id] != float('inf') and dist[id] > max_d:
                    max_d = dist[id]
                    furthest_id = id
            return furthest_id, max_d

        A_geo, _ = get_furthest(comp[0])
        B_geo, S_geo = get_furthest(A_geo)
        return A_geo, B_geo, S_geo

    def compute_straight_len(comp):
        comp_set = set(comp)
        if not comp: return 0
        
        def is_inside(x, y):
            ix, iy = math.floor(x), math.floor(y)
            if ix < 0 or iy < 0 or ix >= width or iy >= height: return False
            return province_map[iy * width + ix] in comp_set

        best_score = -float('inf')
        best_len = 0
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
                    best_len = dist
        return best_len

    def run_case(comp, name):
        A, B, S_geo = compute_extremities(comp)
        L_straight = compute_straight_len(comp)
        SR = L_straight / S_geo if S_geo > 0 else 0
        print(f"{name}:")
        print(f"  Provinces count: {len(comp)}")
        print(f"  Geodesic Dist: {S_geo:.2f}")
        print(f"  Straight Dist: {L_straight:.2f}")
        print(f"  SR: {SR:.4f}")
        
    run_case(gb_all, "Great Britain (All)")
    run_case(england_and_wales, "England + Wales (No Scotland)")
    run_case(england_alone, "England Alone (No Scotland, No Wales)")
    
    # England + Wales without East Anglia (Norfolk)
    england_wales_no_ea = [id for id in england_and_wales if id not in east_anglia_ids]
    run_case(england_wales_no_ea, "England + Wales (No East Anglia)")

    # England Alone without East Anglia (Norfolk)
    england_alone_no_ea = [id for id in england_alone if id not in east_anglia_ids]
    run_case(england_alone_no_ea, "England Alone (No East Anglia)")

analyze()
