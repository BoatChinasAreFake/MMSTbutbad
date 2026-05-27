from PIL import Image

idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

print("--- France longitude (x = 2975) land regions ---")
print("Index map non-water Y coords:")
for y in range(2560):
    p = idx_img.getpixel((2975, y))
    # water centers are handled, let's just see where it's not black/water in index
    if p != (0, 0, 0):
        # Let's print start and end of ranges to keep it short
        pass

# Let's write a smarter search that prints color segments for both images
def print_segments(img, x, name):
    segments = []
    current_color = None
    start_y = 0
    for y in range(2560):
        c = img.getpixel((x, y))
        # If it's ocean color (61, 83, 114) or black (0,0,0) or similar
        is_water = c == (61, 83, 114) or c == (0, 0, 0)
        status = "water" if is_water else f"land {c}"
        if status != current_color:
            if current_color is not None:
                segments.append((start_y, y - 1, current_color))
            current_color = status
            start_y = y
    segments.append((start_y, 2559, current_color))
    
    print(f"\nSegments for {name} at x = {x}:")
    for start, end, col in segments:
        if "land" in col:
            print(f"  y = {start:4d} to {end:4d}: {col}")

print_segments(idx_img, 2975, "Index Map France")
print_segments(un_img, 2975, "UN Map France")

print_segments(idx_img, 4430, "Index Map Australia")
print_segments(un_img, 4430, "UN Map Australia")
