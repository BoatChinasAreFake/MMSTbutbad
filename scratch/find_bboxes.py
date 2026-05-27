from PIL import Image

def get_bboxes():
    img = Image.open('provinces.png')
    pixels = img.convert('RGBA').load()
    width, height = img.size

    for target_key in [25238015, 28985087]:
        pxs = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
                if key == target_key:
                    pxs.append((x, y))
        if pxs:
            min_x = min(p[0] for p in pxs)
            max_x = max(p[0] for p in pxs)
            min_y = min(p[1] for p in pxs)
            max_y = max(p[1] for p in pxs)
            print(f"Key={target_key}: size={len(pxs)}, BBox X:[{min_x}, {max_x}], Y:[{min_y}, {max_y}]")

if __name__ == '__main__':
    get_bboxes()
