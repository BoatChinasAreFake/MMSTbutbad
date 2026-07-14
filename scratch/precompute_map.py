import sys
import json
import os
import math
from PIL import Image

def precompute():
    img_path = 'provinces.png'
    meta_path = 'provinces_meta.json'
    index_img_path = 'provinces_index.png'
    straits_path = 'straits.json'
    definitions_path = 'definitions.json'

    if not os.path.exists(img_path):
        print(f"Error: {img_path} not found in current directory.")
        return

    print("Loading provinces.png...")
    img = Image.open(img_path)
    width, height = img.size
    pixels = img.convert('RGBA').load()

    print(f"Map dimensions: {width}x{height} pixels.")
    
    # Load definitions.json if it exists, otherwise initialize empty
    definitions = {}
    color_to_id = {} # (r, g, b) -> stable_id (int)
    if os.path.exists(definitions_path):
        print(f"Loading province definitions from {definitions_path}...")
        try:
            with open(definitions_path, 'r') as f:
                definitions = json.load(f)
                for id_str, data in definitions.items():
                    r, g, b = data["color"]
                    color_to_id[(r, g, b)] = int(id_str)
            print(f"Loaded {len(definitions)} defined provinces.")
        except Exception as e:
            print(f"Warning: Failed to load definitions.json: {e}")

    # Load water.json if it exists, for initial migration to definitions
    water_set = set()
    water_path = 'water.json'
    if os.path.exists(water_path):
        print(f"Loading water.json for migration...")
        try:
            with open(water_path, 'r') as f:
                water_list = json.load(f)
                water_set = set(int(k) for k in water_list)
        except Exception as e:
            print(f"Warning: Failed to load water.json: {e}")

    # Scan pixels for unique provinces
    print("Scanning pixels for unique provinces...")
    province_centers = {} # stable_id (int) -> {sumX, sumY, count}
    province_map = [0] * (width * height) # flat list of stable IDs
    
    next_id = 1
    if color_to_id:
        next_id = max(color_to_id.values()) + 1

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            color_key = (r, g, b)
            
            # Map background border pixels (usually pure black or transparent) if needed,
            # but usually we treat every color as a province.
            if color_key not in color_to_id:
                # Assign new stable ID
                prov_id = next_id
                color_to_id[color_key] = prov_id
                
                # Check if this raw 32-bit key is in the legacy water_set
                key_32 = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
                is_water = key_32 in water_set
                
                definitions[str(prov_id)] = {
                    "color": [r, g, b],
                    "name": f"Province {prov_id}",
                    "type": "water" if is_water else "land",
                    "terrain": "water" if is_water else "plains"
                }
                next_id += 1
            
            prov_id = color_to_id[color_key]
            province_map[y * width + x] = prov_id
            
            if prov_id not in province_centers:
                province_centers[prov_id] = {
                    "sumX": 0,
                    "sumY": 0,
                    "count": 0
                }
            
            province_centers[prov_id]["sumX"] += x
            province_centers[prov_id]["sumY"] += y
            province_centers[prov_id]["count"] += 1

    print(f"Total provinces: {len(definitions)} (next available ID: {next_id})")

    # Save updated definitions.json
    print(f"Saving definitions.json...")
    with open(definitions_path, 'w') as f:
        json.dump(definitions, f, indent=2)

    # Calculate center of mass coordinates
    final_centers = {}
    for prov_id, data in province_centers.items():
        count = data["count"]
        id_str = str(prov_id)
        
        # Determine water flag from definitions
        is_water = False
        if id_str in definitions:
            is_water = definitions[id_str].get("type") == "water"

        final_centers[id_str] = {
            "index": prov_id,
            "x": round(data["sumX"] / count),
            "y": round(data["sumY"] / count),
            "count": count,
            "is_water": is_water
        }

    # Compute natural neighbors
    print("Computing natural neighbors...")
    province_neighbors = {str(prov_id): set() for prov_id in province_centers.keys()}

    for y in range(height):
        for x in range(width):
            prov_id_a = province_map[y * width + x]
            key_a = str(prov_id_a)

            if x + 1 < width:
                prov_id_b = province_map[y * width + (x + 1)]
                if prov_id_a != prov_id_b:
                    key_b = str(prov_id_b)
                    province_neighbors[key_a].add(key_b)
                    province_neighbors[key_b].add(key_a)

            if y + 1 < height:
                prov_id_b = province_map[(y + 1) * width + x]
                if prov_id_a != prov_id_b:
                    key_b = str(prov_id_b)
                    province_neighbors[key_a].add(key_b)
                    province_neighbors[key_b].add(key_a)

    # Convert neighbors sets to sorted lists for JSON serialization
    final_neighbors = {k: sorted(list(v)) for k, v in province_neighbors.items()}

    # Merge custom straits if straits.json exists
    if os.path.exists(straits_path):
        print(f"Loading custom straits from {straits_path}...")
        try:
            with open(straits_path, 'r') as f:
                straits = json.load(f)
                count_straits = 0
                for strait in straits:
                    if isinstance(strait, dict) and "from" in strait and "to" in strait:
                        key_a_raw, key_b_raw = strait["from"], strait["to"]
                    elif isinstance(strait, (list, tuple)) and len(strait) == 2:
                        key_a_raw, key_b_raw = strait[0], strait[1]
                    else:
                        continue
                    
                    # Helper to map 32-bit key to stable ID
                    def get_stable_id_for_key_32(k32):
                        r = (k32 >> 24) & 0xFF
                        g = (k32 >> 16) & 0xFF
                        b = (k32 >> 8) & 0xFF
                        return color_to_id.get((r, g, b))

                    id_a = get_stable_id_for_key_32(key_a_raw) or key_a_raw
                    id_b = get_stable_id_for_key_32(key_b_raw) or key_b_raw
                    
                    key_a, key_b = str(id_a), str(id_b)
                    if key_a in final_neighbors and key_b in final_neighbors:
                        if key_b not in final_neighbors[key_a]:
                            final_neighbors[key_a].append(key_b)
                            final_neighbors[key_b].append(key_a)
                            count_straits += 1
                print(f"Successfully integrated {count_straits} custom straits.")
        except Exception as e:
            print(f"Warning: Failed to load straits.json: {e}")

    # Write provinces_meta.json (including definitions directly)
    print(f"Writing {meta_path}...")
    meta_data = {
        "province_count": next_id, # max ID + 1 for WebGL index count compatibility
        "definitions": definitions,
        "centers": final_centers,
        "neighbors": final_neighbors
    }
    with open(meta_path, 'w') as f:
        json.dump(meta_data, f, indent=2)

    # Create provinces_index.png
    print(f"Creating encoded index texture: {index_img_path}...")
    index_img = Image.new('RGBA', (width, height))
    index_pixels = index_img.load()

    for y in range(height):
        for x in range(width):
            prov_id = province_map[y * width + x]
            # Encode sequential province ID into RGB channels
            r = prov_id & 0xFF
            g = (prov_id >> 8) & 0xFF
            b = (prov_id >> 16) & 0xFF
            a = 255 # Full opacity
            index_pixels[x, y] = (r, g, b, a)

    index_img.save(index_img_path)
    print(f"Pre-computation complete! Output files generated: {meta_path}, {index_img_path}")

if __name__ == '__main__':
    precompute()
