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

    # GB connected
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

    # Standalone England (excluding Scotland - top 12 GB provinces by Y)
    gb_sorted_by_y = sorted(gb_all, key=lambda id: province_centers[id]["y"])
    scotland_ids = set(gb_sorted_by_y[:12])
    england = [id for id in gb_all if id not in scotland_ids]

    comp = england
    comp_set = set(comp)

    # 1. Geodesic extremities
    def run_dijkstra(start_id):
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
        return dist

    dist1 = run_dijkstra(comp[0])
    A_geo = max(comp, key=lambda id: dist1[id])
    dist2 = run_dijkstra(A_geo)
    B_geo = max(comp, key=lambda id: dist2[id])
    S_geo = dist2[B_geo]

    # Dijkstra path
    dist = {id: float('inf') for id in comp}
    prev = {}
    dist[A_geo] = 0
    pq = [(0, A_geo)]
    while pq:
        pq.sort(key=lambda x: x[0])
        curr_cost, curr = pq.pop(0)
        if curr == B_geo: break
        for n in neighbors.get(curr, []):
            if n not in comp_set: continue
            next_cost = curr_cost + 1
            if next_cost < dist[n]:
                dist[n] = next_cost
                prev[n] = curr
                pq.append((next_cost, n))
    path_ids = []
    cur = B_geo
    while cur is not None:
        path_ids.append(cur)
        cur = prev.get(cur)
    path_ids.reverse()

    path = [[province_centers[id]["x"], province_centers[id]["y"]] for id in path_ids]
    P0 = path[0]
    P3 = path[-1]

    path_lengths = [0]
    for i in range(1, len(path)):
        path_lengths.append(path_lengths[-1] + math.hypot(path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]))
    path_total_len = path_lengths[-1]

    def get_path_point_at(dist_val):
        for i in range(1, len(path_lengths)):
            if path_lengths[i] >= dist_val:
                a = path[i-1]
                b = path[i]
                t = (dist_val - path_lengths[i-1]) / (path_lengths[i] - path_lengths[i-1] or 1)
                return [a[0] * (1-t) + b[0] * t, a[1] * (1-t) + b[1] * t]
        return list(path[-1])

    M_dijkstra = get_path_point_at(path_total_len * 0.5)
    M_straight = [(P0[0] + P3[0]) / 2, (P0[1] + P3[1]) / 2]

    # Calculate tension
    SR = 103.08 / S_geo
    tension = min(0.45, max(0.0, (0.88 - SR) * 8.0))
    print(f"SR: {SR:.3f}, Tension: {tension:.3f}")

    M = [
        (1 - tension) * M_straight[0] + tension * M_dijkstra[0],
        (1 - tension) * M_straight[1] + tension * M_dijkstra[1]
    ]

    vx = M_dijkstra[0] - M_straight[0]
    vy = M_dijkstra[1] - M_straight[1]
    v_len = math.hypot(vx, vy)
    ux = vx / v_len
    uy = vy / v_len

    # Projection to find C
    best_id = comp[0]
    max_proj = -float('inf')
    for id in comp:
        p = province_centers[id]
        proj = (p["x"] - M_straight[0]) * ux + (p["y"] - M_straight[1]) * uy
        if proj > max_proj:
            max_proj = proj
            best_id = id
    pC = province_centers[best_id]

    # Pull midpoint
    pull = 0.30
    M[0] = (1 - pull) * M[0] + pull * pC["x"]
    M[1] = (1 - pull) * M[1] + pull * pC["y"]

    P1 = [
        2 * M[0] - (P0[0] + P3[0]) / 2,
        2 * M[1] - (P0[1] + P3[1]) / 2
    ]

    # Spine
    spine = []
    for i in range(80):
        t = i / 79
        mt = 1 - t
        x = mt*mt * P0[0] + 2*mt*t * P1[0] + t*t * P3[0]
        y = mt*mt * P0[1] + 2*mt*t * P1[1] + t*t * P3[1]
        spine.append([x, y])

    # Check land coverage for different shift values
    def is_inside(x, y):
        ix, iy = math.floor(x), math.floor(y)
        if ix < 0 or iy < 0 or ix >= width or iy >= height: return False
        return province_map[iy * width + ix] in comp_set

    for shift in [0, 10, 15, 20, 25]:
        shx = ux * shift
        shy = uy * shift
        outside = 0
        for pt in spine:
            sx = pt[0] + shx
            sy = pt[1] + shy
            if not is_inside(sx, sy):
                outside += 1
        print(f"Shift: {shift:2d} -> Outside: {outside}/80")

simulate()
