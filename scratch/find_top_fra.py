from PIL import Image

idx_img = Image.open("provinces_index.png").convert("RGB")

segments = []
current_color = None
start_y = 0
for y in range(1280):
    c = idx_img.getpixel((2975, y))
    is_water = c == (0, 0, 0)
    status = "water" if is_water else f"land {c}"
    if status != current_color:
        if current_color is not None:
            segments.append((start_y, y - 1, current_color))
        current_color = status
        start_y = y
segments.append((start_y, 1279, current_color))

print("Top-half segments of Index Map France:")
for start, end, col in segments:
    if "land" in col:
        print(f"  y = {start:4d} to {end:4d}: {col}")
