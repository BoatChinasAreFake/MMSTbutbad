import sys
import math
import random
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

    # 2-pass Dijkstra
    comp = gb_all
    comp_set = set(comp)

    # Dijkstra helper
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

    # Pick a random starting province (e.g. Wales or Midlands)
    start_rand = comp[len(comp) // 2]
    dist1 = run_dijkstra(start_rand)
    
    # Furthest from start is A
    A_geo = max(comp, key=lambda id: dist1[id])
    
    # Furthest from A is B
    dist2 = run_dijkstra(A_geo)
    B_geo = max(comp, key=lambda id: dist2[id])

    print(f"Random Start: ID={start_rand}")
    print(f"A_geo (furthest from start): ID={A_geo}, Center=({province_centers[A_geo]['x']}, {province_centers[A_geo]['y']})")
    print(f"B_geo (furthest from A_geo): ID={B_geo}, Center=({province_centers[B_geo]['x']}, {province_centers[B_geo]['y']})")
    print(f"Geodesic Distance: {dist2[B_geo]:.2f}")

simulate()
