from PIL import Image

def analyze_all():
    img = Image.open('provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

    # Group pixels by key
    by_key = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            if key not in by_key:
                by_key[key] = []
            by_key[key].append((x, y))

    print(f"Total unique keys: {len(by_key)}")

    # Check components for each key
    disjoint_provinces = []
    for key, pxs in by_key.items():
        px_set = set(pxs)
        visited = set()
        components = []
        for px, py in pxs:
            if (px, py) in visited:
                continue
            comp = []
            queue = [(px, py)]
            visited.add((px, py))
            while queue:
                cx, cy = queue.pop(0)
                comp.append((cx, cy))
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = cx + dx, cy + dy
                    if (nx, ny) in px_set and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
            components.append(comp)
        
        if len(components) > 1:
            disjoint_provinces.append((key, components))

    print(f"Found {len(disjoint_provinces)} keys with disjoint components:")
    for key, comps in sorted(disjoint_provinces, key=lambda x: len(x[1]), reverse=True):
        print(f"Key={key}, components={len(comps)}, total_pixels={len(by_key[key])}")
        for i, comp in enumerate(comps[:5]):
            min_x = min(p[0] for p in comp)
            max_x = max(p[0] for p in comp)
            min_y = min(p[1] for p in comp)
            max_y = max(p[1] for p in comp)
            print(f"  Comp {i}: size={len(comp)}, bbox X:[{min_x}, {max_x}], Y:[{min_y}, {max_y}]")
        if len(comps) > 5:
            print("  ...")

if __name__ == '__main__':
    analyze_all()
