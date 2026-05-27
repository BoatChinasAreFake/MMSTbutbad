from PIL import Image

idx = Image.open("provinces_index.png").convert("RGB")
un = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

# Province 3838 color in index map:
# ID = 3838 = 254 + 14 * 256 + 0 * 65536 -> (254, 14, 0)
target_color = (254, 14, 0)

print("Searching for color (254, 14, 0) in provinces_index.png...")
# Let's find some pixels that have this color in provinces_index.png
for y in range(2560):
    for x in range(5120):
        if idx.getpixel((x, y)) == target_color:
            print(f"Found at PIL coordinate: ({x}, {y})")
            print("  UN map color at this coordinate:", un.getpixel((x, y)))
            break
    else:
        continue
    break
