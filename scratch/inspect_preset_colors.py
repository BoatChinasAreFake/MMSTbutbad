import json
from PIL import Image

def inspect():
    preset_img_path = r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png"
    img = Image.open(preset_img_path)
    palette = img.getpalette()
    
    # Let's sample a few points in the USA (North America: x=1000..1500, y=600..900)
    # and Italy (Europe: x=2650, y=950)
    coords = [
        ("USA 1", 1200, 750),
        ("USA 2", 1300, 800),
        ("Italy 1", 2630, 950),
        ("Italy 2", 2640, 960)
    ]
    
    for name, x, y in coords:
        idx = img.getpixel((x, y))
        r = palette[idx*3]
        g = palette[idx*3+1]
        b = palette[idx*3+2]
        print(f"{name} at ({x}, {y}) color index {idx} -> RGB [{r}, {g}, {b}]")

if __name__ == '__main__':
    inspect()
