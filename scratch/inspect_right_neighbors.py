from PIL import Image

def inspect_neighbors():
    img = Image.open('provinces.png')
    pixels = img.convert('RGBA').load()
    width, height = img.size

    for key in [722662655, 723619839]:
        pxs = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                k = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
                if k == key:
                    pxs.append((x, y))
        min_x = min(p[0] for p in pxs)
        max_x = max(p[0] for p in pxs)
        min_y = min(p[1] for p in pxs)
        max_y = max(p[1] for p in pxs)
        print(f"Key={key}: size={len(pxs)}, bbox X:[{min_x}, {max_x}], Y:[{min_y}, {max_y}]")

if __name__ == '__main__':
    inspect_neighbors()
