import json
from PIL import Image
import os

TERRAINS_LIST = [
    "abyssal_trench",
    "abyss",
    "ocean_depths",
    "ocean_basin",
    "continental_shelf",
    "coastal_waters",

    "monsoon_subtropical_floodplains",
    "monsoon_subtropical_flatlands",
    "monsoon_subtropical_rolling_hills",
    "monsoon_subtropical_foothills",
    "monsoon_subtropical_mountains",

    "high_mountains",

    "monsoon_subtropical_forest_floodplains",
    "monsoon_subtropical_forest_flatlands",
    "monsoon_subtropical_forest_rolling_hill",
    "monsoon_subtropical_forest_foothills",
    "monsoon_subtropical_forest_mountains",

    "arid_floodplains",
    "arid_flatlands",
    "arid_rolling_hills",
    "arid_foothills",
    "arid_mountains",

    "semi_arid_floodplains",
    "semi_arid_flatlands",
    "semi_arid_rolling_hills",
    "semi_arid_foothills",
    "semi_arid_mountains",

    "tropical_monsoon_floodplains",
    "tropical_monsoon_flatlands",
    "tropical_monsoon_rolling_hills",

    "tropical_rainforest_floodplains",
    "tropical_rainforest_flatlands",
    "tropical_rainforest_rolling_hills",
    "tropical_rainforest_foothills",
    "tropical_rainforest_mountains",

    "permafrost_floodplains",
    "permafrost_flatlands",
    "permafrost_rolling_hills",
    "permafrost_foothills",
    "permafrost_mountains",

    "tundra_floodplains",
    "tundra_flatlands",
    "tundra_rolling_hills",
    "tundra_foothills",
    "tundra_mountains",

    "taiga_floodplains",
    "taiga_flatlands",
    "taiga_rolling_hills",
    "taiga_foothills",
    "taiga_mountains",

    "continental_floodplains",
    "continental_flatlands",
    "continental_rolling_hills",
    "continental_foothills",
    "continental_mountains",

    "continental_forest_floodplains",
    "continental_forest_flatlands",
    "continental_forest_rolling_hills",
    "continental_forest_foothills",
    "continental_forest_mountains",

    "temperate_floodplains",
    "temperate_flatlands",
    "temperate_rolling_hills",
    "temperate_foothills",
    "temperate_mountains",

    "temperate_forest_floodplains",
    "temperate_forest_flatlands",
    "temperate_forest_rolling_hills",
    "temperate_forest_foothills",
    "temperate_forest_mountains",

    "mediterranean_floodplains",
    "mediterranean_flatlands",
    "mediterranean_rolling_hills",
    "mediterranean_foothills",
    "mediterranean_mountains",

    "mediterranean_forest_floodplains",
    "mediterranean_forest_flatlands",
    "mediterranean_forest_rolling_hills",
    "mediterranean_forest_foothills",
    "mediterranean_forest_mountains"
]

ORIGINAL_COLORS = [
    [25, 25, 112], [20, 47, 130], [15, 68, 148], [10, 90, 166], [5, 111, 184], [0, 133, 202],
    [255, 140, 0], [255, 110, 0], [255, 79, 0], [120, 81, 169], [99, 62, 151], [78, 42, 132],
    [0, 159, 107], [0, 122, 82], [0, 86, 58], [0, 49, 33], [0, 40, 20],
    [218, 221, 152], [189, 187, 135], [159, 153, 117], [130, 118, 100], [100, 84, 82],
    [255, 211, 0], [219, 175, 5], [184, 139, 10], [148, 102, 15], [112, 66, 20],
    [237, 27, 36], [194, 14, 30], [150, 0, 24],
    [150, 184, 93], [124, 157, 69], [110, 139, 61], [82, 104, 45], [68, 86, 38],
    [171, 195, 227], [157, 185, 222], [143, 175, 217], [129, 165, 213], [115, 155, 208],
    [168, 213, 186], [127, 184, 153], [79, 140, 106], [47, 101, 77], [22, 58, 45],
    [216, 226, 220], [182, 195, 190], [144, 159, 154], [108, 122, 118], [75, 88, 84],
    [232, 217, 168], [210, 183, 127], [176, 143, 89], [136, 105, 65], [94, 71, 46],
    [200, 230, 181], [156, 204, 129], [106, 156, 93], [78, 114, 66], [51, 76, 43],
    [195, 203, 182], [165, 173, 146], [128, 141, 112], [95, 108, 85], [62, 70, 57],
    [175, 205, 178], [136, 173, 138], [100, 137, 107], [70, 103, 80], [44, 69, 56],
    [195, 203, 182], [165, 173, 146], [128, 141, 112], [95, 108, 85], [62, 70, 57],
    [175, 205, 178], [136, 173, 138], [100, 137, 107], [70, 103, 80], [44, 69, 56]
]

def map_detailed_to_simple(name):
    # Determine base simplified category
    if name in ["abyssal_trench", "abyss", "ocean_depths", "ocean_basin", "continental_shelf", "coastal_waters"]:
        return "water"
    
    if "mountains" in name or "mountain" in name or name == "high_mountains":
        return "mountain"
        
    if "rolling_hills" in name or "rolling_hill" in name or "foothills" in name:
        return "hills"
        
    if "forest" in name or "taiga" in name:
        return "forest"
        
    if "floodplains" in name:
        return "marsh"
        
    return "plains"

def apply_terrains():
    prov_img_path = 'provinces.png'
    terr_img_path = 'terrain.png'
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
    
    palette = terr_img.getpalette()
    if not palette:
        print("Error: terrain.png has no color palette.")
        return

    # Map each PNG palette index to a detailed terrain name based on RGB match to ORIGINAL_COLORS
    idx_to_detailed_name = {}
    num_palette_colors = len(palette) // 3
    
    for i in range(num_palette_colors):
        pr = palette[i*3]
        pg = palette[i*3+1]
        pb = palette[i*3+2]
        
        # Check if it's black/unknown (often index 0 or fallback)
        if pr == 0 and pg == 0 and pb == 0:
            idx_to_detailed_name[i] = "unknown"
            continue
            
        # Find closest match in ORIGINAL_COLORS
        best_match_idx = -1
        min_diff = 999999
        for oc_idx, oc in enumerate(ORIGINAL_COLORS):
            diff = abs(pr - oc[0]) + abs(pg - oc[1]) + abs(pb - oc[2])
            if diff < min_diff:
                min_diff = diff
                best_match_idx = oc_idx
                
        if min_diff < 10: # Close match threshold
            idx_to_detailed_name[i] = TERRAINS_LIST[best_match_idx]
        else:
            idx_to_detailed_name[i] = "unknown"

    print("Loading definitions.json...")
    with open(definitions_path, 'r') as f:
        definitions = json.load(f)
        
    color_to_id = {}
    for id_str, d in definitions.items():
        color_to_id[tuple(d["color"])] = id_str

    print("Accumulating pixel terrain indices for each province...")
    province_pixels = {}
    for y in range(height):
        for x in range(width):
            p_color = prov_pix[x, y]
            prov_id = color_to_id.get(p_color)
            if prov_id:
                terr_idx = terr_pix[x, y]
                if prov_id not in province_pixels:
                    province_pixels[prov_id] = {}
                province_pixels[prov_id][terr_idx] = province_pixels[prov_id].get(terr_idx, 0) + 1

    print("Applying exact terrain mappings...")
    water_count = 0
    land_count = 0
    unknown_count = 0
    
    for prov_id, counts in province_pixels.items():
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        dominant_idx = sorted_counts[0][0]
        
        detailed_name = idx_to_detailed_name.get(dominant_idx, "unknown")
        
        # If it is unknown, we can fall back to plains/water based on simple rules or keep it unknown
        if detailed_name == "unknown":
            unknown_count += 1
            terrain_type = "plains"
        else:
            terrain_type = map_detailed_to_simple(detailed_name)
            
        is_water = (terrain_type == "water")
        prov_type = "water" if is_water else "land"
        
        definitions[prov_id]["type"] = prov_type
        definitions[prov_id]["terrain"] = terrain_type
        definitions[prov_id]["detailed_terrain"] = detailed_name
        
        if is_water:
            water_count += 1
        else:
            land_count += 1

    print(f"Total provinces updated: {len(province_pixels)} (Land: {land_count}, Water: {water_count}, Unknown: {unknown_count})")
    
    print("Saving definitions.json...")
    with open(definitions_path, 'w') as f:
        json.dump(definitions, f, indent=2)

if __name__ == '__main__':
    apply_terrains()
