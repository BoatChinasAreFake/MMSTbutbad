import math
from PIL import Image

def generate_map():
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
    gb_all = set()
    while queue:
        curr = queue.pop(0)
        gb_all.add(curr)
        for n in neighbors.get(curr, []):
            if n in land_set and n not in visited:
                n_center = province_centers[n]
                if n_center["x"] > 75: # filter out Ireland/isle of man
                    visited.add(n)
                    queue.append(n)

    # Print a grid from x=75 to 195, y=0 to 95
    grid_w = 40
    grid_h = 35
    print("Great Britain Province Map (Text Grid):")
    for gy in range(grid_h):
        y = int(gy * (100 / grid_h))
        row = ""
        for gx in range(grid_w):
            x = int(75 + gx * (120 / grid_w))
            pid = province_map[y * width + x]
            if pid in gb_all:
                # print a single char representing the province
                # We can use the last digit of the ID
                row += str(pid % 10)
            else:
                row += "."
        print(f"y={y:2d} | {row}")

generate_map()
