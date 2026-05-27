from PIL import Image
import json

def inspect_ireland():
    img = Image.open('provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

    # Load water.json
    with open('water.json', 'r') as f:
        water_keys = set(json.load(f))

    # Let's find all unique keys inside Ireland: X in [0, 80], Y in [0, 80]
    ireland_keys = set()
    for y in range(80):
        for x in range(80):
            r, g, b, a = pixels[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            ireland_keys.add(key)

    print("Provinces in Ireland area:")
    for key in sorted(list(ireland_keys)):
        is_water = key in water_keys
        # Count pixels of this key in Ireland area vs entire map
        in_ireland_count = 0
        total_count = 0
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                k = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
                if k == key:
                    total_count += 1
                    if x < 80 and y < 80:
                        in_ireland_count += 1
        
        # Print info
        water_status = "WATER" if is_water else "LAND"
        print(f"  Key={key:10d}, color=({(key>>24)&255}, {(key>>16)&255}, {(key>>8)&255}, {key&255}), status={water_status}, in_ireland={in_ireland_count}/{total_count}")

if __name__ == '__main__':
    inspect_ireland()
