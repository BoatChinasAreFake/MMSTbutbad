from PIL import Image

def find_shapes():
    img = Image.open('provinces.png')
    pixels = img.convert('RGBA').load()
    width, height = img.size

    for key in [722662655, 723619839]:
        print(f"\nShape for Key {key}:")
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
        
        # Print text grid of this province
        for y in range(min_y, max_y + 1):
            row = []
            for x in range(min_x, max_x + 1):
                if (x, y) in pxs:
                    row.append("#")
                else:
                    row.append(".")
            print("".join(row))

if __name__ == '__main__':
    find_shapes()
