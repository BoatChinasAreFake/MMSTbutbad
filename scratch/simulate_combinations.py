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
                if n_center["x"] > 75: # filter out Ireland/isle of man
                    visited.add(n)
                    queue.append(n)

    # Now let's classify provinces:
    # Scotland is north: y < 45
    # Wales is west: x < 125 and y between 48 and 80
    # England is the rest of GB (x >= 125 or y >= 80 or y >= 45)
    
    scotland = [id for id in gb_all if province_centers[id]["y"] < 45]
    wales = [id for id in gb_all if province_centers[id]["x"] < 123 and 45 <= province_centers[id]["y"] <= 80]
    
    # Norfolk / East Anglia: x > 165 and 55 <= y <= 75
    norfolk = [id for id in gb_all if province_centers[id]["x"] > 165 and 55 <= province_centers[id]["y"] <= 75]
    
    # England alone (excluding Scotland and Wales)
    england = [id for id in gb_all if id not in scotland and id not in wales]
    # England + Wales (excluding Scotland)
    england_wales = [id for id in gb_all if id not in scotland]

    def test_component(comp, name):
        comp_set = set(comp)
        if len(comp) < 2:
            print(f"{name}: Empty or too small")
            return

        # Calculate depth (distance to boundary)
        depth = {}
        depth_queue = []
        for id in comp:
            is_boundary = False
            for n in neighbors[id]:
                if n not in comp_set:
                    is_boundary = True
                    break
            if is_boundary:
                depth[id] = 1
                depth_queue.append(id)
        if not depth_queue:
            depth[comp[0]] = 1
            depth_queue.append(comp[0])
        while depth_queue:
            curr = depth_queue.pop(0)
            curr_depth = depth[curr]
            for n in neighbors[curr]:
                if n in comp_set and n not in depth:
                    depth[n] = curr_depth + 1
                    depth_queue.append(n)

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

        A_geo, _ = get_furthest(comp[0])
        B_geo, S_geo = get_furthest(A_geo)

        # Optimal straight line
        def is_inside(x, y):
            ix, iy = math.floor(x), math.floor(y)
            if ix < 0 or iy < 0 or ix >= width or iy >= height: return False
            return province_map[iy * width + ix] in comp_set

        best_score = -float('inf')
        L_straight = 0
        A_straight = comp[0]
        B_straight = comp[0]

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
                    A_straight = idA
                    B_straight = idB
                    L_straight = dist

        SR = L_straight / S_geo if S_geo > 0 else 0
        
        # Output
        print(f"\n=== {name} ===")
        print(f"  Provinces: {len(comp)}")
        print(f"  Geodesic endpoints: {A_geo} -> {B_geo} (dist = {S_geo:.2f})")
        print(f"  Straight endpoints: {A_straight} -> {B_straight} (dist = {L_straight:.2f})")
        print(f"  SR: {SR:.4f}")

    test_component(gb_all, "Great Britain Connected")
    test_component(england_wales, "England + Wales (excluding Scotland)")
    test_component(england, "England Alone (excluding Scotland & Wales)")
    
    # England Alone without Norfolk (East Anglia)
    england_no_norfolk = [id for id in england if id not in norfolk]
    test_component(england_no_norfolk, "England Alone (No Norfolk)")

    # England + Wales without Norfolk (East Anglia)
    england_wales_no_norfolk = [id for id in england_wales if id not in norfolk]
    test_component(england_wales_no_norfolk, "England + Wales (No Norfolk)")

run_simulation()
