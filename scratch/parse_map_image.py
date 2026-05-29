import os
import json
import numpy as np
from PIL import Image

def main():
    # Exclude water provinces & load coordinates
    water_provs = set()
    if os.path.exists("provinces_meta.json"):
        with open("provinces_meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        for pid_str, center_data in meta.get("centers", {}).items():
            pid = int(pid_str)
            if center_data.get("is_water") or center_data.get("is_lake"):
                water_provs.add(pid)
    print(f"Loaded {len(water_provs)} water provinces to exclude.")

    index_path = "provinces_index.png"
    un_map_path = r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png"
    
    print("Loading image arrays...")
    idx_img = Image.open(index_path).convert("RGB")
    un_img = Image.open(un_map_path).convert("RGB")
    
    idx_arr = np.array(idx_img, dtype=np.uint32)
    un_arr = np.array(un_img, dtype=np.uint8)
    
    prov_ids = idx_arr[:, :, 0] + idx_arr[:, :, 1] * 256 + idx_arr[:, :, 2] * 65536
    
    flat_ids = prov_ids.reshape(-1)
    flat_colors = un_arr.reshape(-1, 3)
    
    print("Grouping colors by province ID...")
    unique_ids, indices = np.unique(flat_ids, return_inverse=True)
    
    sums = np.zeros((len(unique_ids), 3), dtype=np.uint64)
    counts = np.zeros(len(unique_ids), dtype=np.uint64)
    
    np.add.at(sums, indices, flat_colors)
    np.add.at(counts, indices, 1)
    
    avg_colors = (sums / counts[:, np.newaxis]).astype(np.uint8)
    
    target_afg_color = np.array([24, 61, 64], dtype=np.float32) # hex 183D40
    ocean_color = np.array([38, 50, 68], dtype=np.float32)
    
    color_groups = {}
    ownership = {}
    
    afg_count = 0
    for idx_item, pid in enumerate(unique_ids):
        pid = int(pid)
        if pid == 0 or pid in water_provs:
            continue
            
        p_color = avg_colors[idx_item]
        
        # If the land province matches the 183D40 (unowned/grey) color, assign it to '196'
        if np.linalg.norm(p_color.astype(np.float32) - target_afg_color) < 15.0:
            ownership[str(pid)] = "196"
            afg_count += 1
            continue
            
        # Ignore actual ocean color if it's not a land province (already checked above)
        if np.linalg.norm(p_color.astype(np.float32) - ocean_color) < 15.0:
            continue
            
        color_key = tuple(int(x) for x in p_color)
        color_groups.setdefault(color_key, []).append(pid)
        
    print(f"Assigned {afg_count} land provinces with color 183D40 to tag '196'.")
    print(f"Grouped remaining land provinces into {len(color_groups)} unique colors.")
    
    # Sort remaining color groups by size to assign tags consistently
    sorted_colors = sorted(color_groups.items(), key=lambda x: len(x[1]), reverse=True)
    
    assigned_countries = {}
    assigned_countries["196"] = {
        "name": "Placeholder 196 (Color 183D40)",
        "color": [24, 61, 64]
    }
    
    for i, (color, pids) in enumerate(sorted_colors):
        # Generate tags like 000, 001, 002, etc. (skipping 196 if it falls in this range)
        tag = f"{i:03d}"
        if tag == "196":
            # Just shift to avoid conflict
            tag = f"{i+1:03d}"
            
        assigned_countries[tag] = {
            "name": f"Placeholder {tag} (Color {color})",
            "color": list(color)
        }
        for pid in pids:
            ownership[str(pid)] = tag
            
    print(f"Assigned {len(color_groups)} colors to {len(assigned_countries) - 1} numeric placeholder tags.")
    
    output_data = {
        "countries": assigned_countries,
        "ownership": ownership
    }
    
    with open("preset_ownership.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    print("Successfully generated preset_ownership.json with exact color matching!")

if __name__ == '__main__':
    main()
