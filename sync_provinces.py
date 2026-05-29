import json
import os
from PIL import Image

def main():
    image_path = "provinces.png"
    index_path = "provinces_index.png"
    meta_path = "provinces_meta.json"
    
    if not os.path.exists(image_path):
        print(f"Error: Could not find provinces.png in the project directory.")
        return
        
    if not os.path.exists(index_path):
        print(f"Error: Could not find provinces_index.png in the project directory.")
        return
        
    if not os.path.exists(meta_path):
        print(f"Error: Could not find {meta_path}")
        return
        
    print(f"Loading display image: {image_path}...")
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = img.load()
    
    print(f"Loading index image: {index_path}...")
    index_img = Image.open(index_path).convert("RGB")
    index_pixels = index_img.load()
    
    print(f"Loading metadata: {meta_path}...")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta_data = json.load(f)
        
    definitions = meta_data.get("definitions", {})
    centers = meta_data.get("centers", {})
    neighbors = meta_data.get("neighbors", {})
    
    # Map colors to ID from existing definitions
    existing_colors = {}
    for prov_id, d in definitions.items():
        color_tuple = tuple(d["color"])
        existing_colors[color_tuple] = int(prov_id)
        
    # Determine the starting ID for new provinces
    max_id = 0
    if definitions:
        max_id = max(int(k) for k in definitions.keys())
        
    print("Scanning display image for colors...")
    # Find all coordinates for each color
    color_pixel_coords = {}
    
    for y in range(height):
        for x in range(width):
            color = pixels[x, y]
            # Ignore pure white (background/borders)
            if color == (255, 255, 255):
                continue
            if color not in color_pixel_coords:
                color_pixel_coords[color] = []
            color_pixel_coords[color].append((x, y))
            
    print(f"Found {len(color_pixel_coords)} unique colors in display image.")
    
    new_provinces_added = 0
    next_id = max_id + 1
    
    # For index assignment
    max_index = -1
    for center_data in centers.values():
        max_index = max(max_index, center_data.get("index", -1))
    next_index = max_index + 1
    
    index_modified = False
    
    for color, coords in color_pixel_coords.items():
        prov_id_int = existing_colors.get(color)
        
        # If it's a new color
        if prov_id_int is None:
            new_id = str(next_id)
            print(f"Adding new province ID {new_id} for color {color}...")
            
            # Calculate center coordinates
            sum_x = sum(pt[0] for pt in coords)
            sum_y = sum(pt[1] for pt in coords)
            center_x = round(sum_x / len(coords), 1)
            center_y = round(sum_y / len(coords), 1)
            
            # Add to definitions
            definitions[new_id] = {
                "color": list(color),
                "name": f"Province {new_id}",
                "type": "land",
                "terrain": "plains",
                "detailed_terrain": "flatlands"
            }
            
            # Add to centers
            centers[new_id] = {
                "x": center_x,
                "y": center_y,
                "count": len(coords),
                "index": next_index,
                "is_water": False
            }
            
            # Initialize empty neighbors entry
            neighbors[new_id] = []
            
            prov_id_int = next_id
            
            next_id += 1
            next_index += 1
            new_provinces_added += 1
            
        # Write the ID-encoded color to provinces_index.png for all its pixel coords
        # ID encoding is: R = id % 256, G = (id // 256) % 256, B = (id // 65536) % 256
        r_enc = prov_id_int % 256
        g_enc = (prov_id_int // 256) % 256
        b_enc = (prov_id_int // 65536) % 256
        encoded_color = (r_enc, g_enc, b_enc)
        
        for (x, y) in coords:
            if index_pixels[x, y] != encoded_color:
                index_pixels[x, y] = encoded_color
                index_modified = True
                
    if new_provinces_added > 0:
        meta_data["province_count"] = len(definitions)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=2)
            
    if index_modified or new_provinces_added > 0:
        print(f"Saving updated index map: {index_path}...")
        index_img.save(index_path)
        print(f"\nSuccess! Registered {new_provinces_added} new provinces and synchronized the index map.")
    else:
        print("\nNo changes or new provinces detected.")

if __name__ == "__main__":
    main()
