import json
from PIL import Image
import os
import subprocess

# Define the palette index mappings to terrain categories
WATER_INDICES = {1, 2, 3, 4, 5, 6, 36, 37, 38, 39, 40}
FOREST_INDICES = {
    13, 14, 15, 16, 17, 31, 32, 33, 34, 35, 43, 44, 45, 
    57, 58, 59, 60, 63, 64, 65, 67, 68, 69, 70, 73, 74, 75, 77, 78, 79, 80
}
MOUNTAIN_INDICES = {46, 47, 48, 49, 50, 61, 62, 66, 71, 72, 76}
HILLS_INDICES = {19, 20, 21, 22, 27, 51, 52, 53, 54, 55}
MARSH_INDICES = {10, 11, 12, 28, 29, 30}

def get_terrain_category(idx):
    if idx in WATER_INDICES:
        return "water"
    elif idx in FOREST_INDICES:
        return "forest"
    elif idx in MOUNTAIN_INDICES:
        return "mountain"
    elif idx in HILLS_INDICES:
        return "hills"
    elif idx in MARSH_INDICES:
        return "marsh"
    else:
        return "plains"

def apply_terrain():
    prov_img_path = 'provinces.png'
    terr_img_path = 'terrain.bmp'
    definitions_path = 'definitions.json'

    if not os.path.exists(prov_img_path) or not os.path.exists(terr_img_path):
        print("Required images not found!")
        return

    print("Loading images...")
    prov_img = Image.open(prov_img_path).convert('RGB')
    terr_img = Image.open(terr_img_path)
    
    width, height = prov_img.size
    prov_pix = prov_img.load()
    terr_pix = terr_img.load()
    
    print("Loading definitions.json...")
    with open(definitions_path, 'r') as f:
        definitions = json.load(f)
        
    color_to_id = {}
    for id_str, d in definitions.items():
        color_to_id[tuple(d["color"])] = id_str

    print("Accumulating pixel terrain indices for each province...")
    province_pixels = {}
    # Sample every pixel for maximum accuracy (since we want precise terrain mapping)
    for y in range(height):
        for x in range(width):
            p_color = prov_pix[x, y]
            prov_id = color_to_id.get(p_color)
            if prov_id:
                terr_idx = terr_pix[x, y]
                if prov_id not in province_pixels:
                    province_pixels[prov_id] = {}
                province_pixels[prov_id][terr_idx] = province_pixels[prov_id].get(terr_idx, 0) + 1

    print("Determining dominant terrain type for each province...")
    updated_count = 0
    water_count = 0
    land_count = 0
    
    for prov_id, counts in province_pixels.items():
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        dominant_idx = sorted_counts[0][0]
        terrain_type = get_terrain_category(dominant_idx)
        
        is_water = (terrain_type == "water")
        prov_type = "water" if is_water else "land"
        
        definitions[prov_id]["type"] = prov_type
        definitions[prov_id]["terrain"] = terrain_type
        
        if is_water:
            water_count += 1
        else:
            land_count += 1
            
        updated_count += 1

    print(f"Total provinces updated: {updated_count} (Land: {land_count}, Water: {water_count})")
    
    print("Saving updated definitions.json...")
    with open(definitions_path, 'w') as f:
        json.dump(definitions, f, indent=2)

if __name__ == '__main__':
    apply_terrain()
