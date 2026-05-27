from PIL import Image

def print_grid():
    img = Image.open('provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

    # Bounding box around Lough Neagh: X:[49, 67], Y:[21, 29]
    # Let's inspect a larger region: X:[35, 75], Y:[15, 35]
    x_start, x_end = 35, 75
    y_start, y_end = 15, 35

    # Find unique keys in this region to assign simple characters
    unique_keys = set()
    for y in range(y_start, y_end):
        for x in range(x_start, x_end):
            r, g, b, a = pixels[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            unique_keys.add(key)

    key_to_char = {}
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz#@$%&"
    for i, key in enumerate(sorted(list(unique_keys))):
        key_to_char[key] = chars[i % len(chars)]

    print("Char mapping:")
    for key, char in key_to_char.items():
        # Identify if it is water/ocean/lake
        water_label = ""
        if key == 4269493503:
            water_label = " (Ocean)"
        elif key == 1661922559:
            water_label = " (Ocean-West)"
        elif key == 28985087:
            water_label = " (Lough Neagh)"
        print(f"  '{char}': Key={key} {water_label}")

    print("\nGrid:")
    for y in range(y_start, y_end):
        row = []
        for x in range(x_start, x_end):
            r, g, b, a = pixels[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            row.append(key_to_char[key])
        print(f"{y:2d}: " + "".join(row))

if __name__ == '__main__':
    print_grid()
