from PIL import Image

def check_regions():
    img = Image.open('provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

    target_key = 1661922559
    target_color = (99, 14, 236, 255)

    # Find all pixels of target_key
    target_pixels = set()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            if key == target_key:
                target_pixels.add((x, y))

    print(f"Total pixels of color {target_color}: {len(target_pixels)}")

    # Run BFS to find connected components
    visited = set()
    components = []

    for px, py in target_pixels:
        if (px, py) in visited:
            continue
        # New component
        comp = []
        queue = [(px, py)]
        visited.add((px, py))
        while queue:
            cx, cy = queue.pop(0)
            comp.append((cx, cy))
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in target_pixels and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        components.append(comp)

    print(f"Found {len(components)} connected components of this color:")
    for i, comp in enumerate(components):
        min_x = min(p[0] for p in comp)
        max_x = max(p[0] for p in comp)
        min_y = min(p[1] for p in comp)
        max_y = max(p[1] for p in comp)
        print(f"  Component {i}: size={len(comp)}, bounding box X:[{min_x}, {max_x}], Y:[{min_y}, {max_y}]")

if __name__ == '__main__':
    check_regions()
