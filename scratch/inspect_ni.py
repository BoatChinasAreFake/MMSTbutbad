from PIL import Image
import json

def inspect():
    img = Image.open('provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

    lough_neagh_key = 28985087
    lough_neagh_pixels = []
    
    # Map pixel to key
    pixel_keys = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            pixel_keys[(x, y)] = key
            if key == lough_neagh_key:
                lough_neagh_pixels.append((x, y))

    print(f"Lough Neagh has {len(lough_neagh_pixels)} pixels.")
    if lough_neagh_pixels:
        min_x = min(p[0] for p in lough_neagh_pixels)
        max_x = max(p[0] for p in lough_neagh_pixels)
        min_y = min(p[1] for p in lough_neagh_pixels)
        max_y = max(p[1] for p in lough_neagh_pixels)
        print(f"Bounding box: X:[{min_x}, {max_x}], Y:[{min_y}, {max_y}]")

    # Find neighbors by scanning pixel boundaries
    neighbors_found = set()
    for x, y in lough_neagh_pixels:
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                nkey = pixel_keys[(nx, ny)]
                if nkey != lough_neagh_key:
                    neighbors_found.add(nkey)

    print("\nNeighbors of Lough Neagh found from pixel scanning:")
    with open('provinces_meta.json', 'r') as f:
        meta = json.load(f)

    for nkey in neighbors_found:
        meta_info = meta["centers"].get(str(nkey), None)
        print(f"Key={nkey}, Meta={meta_info}")

if __name__ == '__main__':
    inspect()
