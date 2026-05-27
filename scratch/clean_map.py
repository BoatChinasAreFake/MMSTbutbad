from PIL import Image
from collections import Counter
import sys

def clean_map():
    print("Loading provinces.png for cleaning...")
    img = Image.open('provinces.png')
    img_rgba = img.convert('RGBA')
    width, height = img.size
    pixels = img_rgba.load()

    print("Counting color occurrences...")
    flat_pixels = []
    for y in range(height):
        for x in range(width):
            flat_pixels.append(pixels[x, y])

    counts = Counter(flat_pixels)
    print(f"Total unique colors detected: {len(counts)}")

    # Define valid colors (size >= 5 pixels)
    valid_colors = {color for color, count in counts.items() if count >= 5}
    print(f"Valid colors (count >= 5): {len(valid_colors)}")

    if len(valid_colors) == 0:
        print("Error: No valid colors found!")
        return

    # Keep track of pixels to clean
    cleaned_pixels = Image.new('RGBA', (width, height))
    cleaned_load = cleaned_pixels.load()

    # Pass 1: Copy valid pixels, mark invalid ones
    invalid_positions = []
    for y in range(height):
        for x in range(width):
            color = pixels[x, y]
            if color in valid_colors:
                cleaned_load[x, y] = color
            else:
                invalid_positions.append((x, y))

    print(f"Number of noisy pixels to fix: {len(invalid_positions)}")

    # Pass 2: Neighbor propagation to fill noisy pixels
    # We do a flood-fill propagation. In each pass, we resolve pixels that have a resolved neighbor.
    resolved_count = 0
    passes = 0
    
    while invalid_positions:
        passes += 1
        print(f"Cleaning pass {passes}... Remaining noisy pixels: {len(invalid_positions)}")
        next_invalid = []
        resolved_in_pass = 0
        
        # We search neighbors
        for x, y in invalid_positions:
            # Check 4 neighbors
            resolved_color = None
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < width and 0 <= ny < height:
                    # If neighbor is already filled in cleaned image
                    n_color = cleaned_load[nx, ny]
                    if n_color != (0, 0, 0, 0): # PIL default is transparent/black for unfilled
                        resolved_color = n_color
                        break
            
            if resolved_color:
                cleaned_load[x, y] = resolved_color
                resolved_in_pass += 1
            else:
                next_invalid.append((x, y))
        
        # If we couldn't resolve any pixels in a pass, break (prevent infinite loop)
        if resolved_in_pass == 0:
            print("Warning: Could not resolve remaining pixels by direct neighbors. Snapping to closest valid color.")
            # Fallback: snap remaining to the absolute closest valid color
            valid_list = list(valid_colors)
            for x, y in next_invalid:
                orig_color = pixels[x, y]
                closest_color = min(valid_list, key=lambda c: sum(abs(i-j) for i,j in zip(c, orig_color)))
                cleaned_load[x, y] = closest_color
            break
            
        invalid_positions = next_invalid

    # Save the cleaned image
    cleaned_pixels.save('provinces.png')
    print("Cleaned provinces.png saved successfully!")

if __name__ == '__main__':
    clean_map()
