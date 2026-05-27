from PIL import Image

un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")
idx_img = Image.open("provinces_index.png").convert("RGB")

# Paris is at (2975, 532) in standard coordinates (top-down)
# If the UN map is vertically flipped, Paris would be at (2975, 2560 - 1 - 532) = (2975, 2027)
print("UN map pixel at Paris (2975, 532):", un_img.getpixel((2975, 532)))
print("UN map pixel at Y-flipped (2975, 2027):", un_img.getpixel((2975, 2027)))

# Let's also check a coordinate in the Southern Hemisphere
# E.g. Melbourne, Australia is around (4432, 2185) in top-down coordinates
# Y-flipped: (4432, 2560 - 1 - 2185) = (4432, 374)
print("\nAustralia Melbourne (4432, 2185):")
print("  Index pixel:", idx_img.getpixel((4432, 2185)))
print("  UN map pixel:", un_img.getpixel((4432, 2185)))
print("  UN map Y-flipped pixel:", un_img.getpixel((4432, 374)))
