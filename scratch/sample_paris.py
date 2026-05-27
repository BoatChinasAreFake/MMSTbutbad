from PIL import Image

idx_img = Image.open("provinces_index.png")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png")

print("Index pixel at (2975, 532):", idx_img.getpixel((2975, 532)))
print("UN map pixel at (2975, 532):", un_img.getpixel((2975, 532)))

# Let's search around (2975, 532) to see the colors in a 10x10 area
print("\n10x10 grid of UN map colors around Paris:")
for dy in range(-5, 5):
    row = []
    for dx in range(-5, 5):
        row.append(un_img.getpixel((2975 + dx, 532 + dy)))
    print("  ", row)
