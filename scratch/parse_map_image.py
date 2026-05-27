import os
import json
import numpy as np
from PIL import Image
import colorsys
import re

def parse_valid_tags():
    tags_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\country_tags"
    valid_tags = set()
    if not os.path.exists(tags_dir):
        return valid_tags
    files = [f for f in os.listdir(tags_dir) if f.endswith('.txt')]
    for fname in files:
        fpath = os.path.join(tags_dir, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = re.match(r'^\s*([A-Z0-9]{3})\s*=', line)
                if match:
                    valid_tags.add(match.group(1).upper())
    return valid_tags

def parse_localisation(valid_tags):
    loc_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\localisation\english"
    names = {}
    if not os.path.exists(loc_dir):
        return names
    for root, dirs, files in os.walk(loc_dir):
        for fname in files:
            if not fname.endswith('.yml'):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8-sig', errors='ignore') as f:
                for line in f:
                    match = re.match(r'^\s*([a-z0-9_]+):\d?\s*"(.*?)"', line, re.IGNORECASE)
                    if match:
                        key = match.group(1).upper()
                        name = match.group(2)
                        if key in valid_tags:
                            names[key] = name
                        else:
                            parts = key.split('_')
                            if len(parts) > 1 and parts[0] in valid_tags:
                                tag = parts[0]
                                if tag not in names or key.endswith('_NEUTRALITY') or key.endswith('_FASCISM') or key.endswith('_DEMOCRATIC') or key.endswith('_NEUTRALITY_DEF') or key.endswith('_FASCISM_DEF') or key.endswith('_DEMOCRATIC_DEF'):
                                    names[tag] = name
    return names

def parse_colors():
    vanilla_path = r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\common\countries\colors.txt"
    mod_path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\countries\colors.txt"
    def parse_colors_file(filepath):
        country_colors = {}
        if not os.path.exists(filepath):
            return country_colors
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        pattern = re.compile(
            r'([A-Z0-9]{3})\s*=\s*\{[^}]*?color\s*=\s*(rgb|hsv)\s*\{\s*([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s*\}', 
            re.DOTALL | re.IGNORECASE
        )
        for match in pattern.finditer(content):
            tag = match.group(1).upper()
            col_type = match.group(2).lower()
            val1 = float(match.group(3))
            val2 = float(match.group(4))
            val3 = float(match.group(5))
            if col_type == 'rgb':
                r = int(round(val1))
                g = int(round(val2))
                b = int(round(val3))
            else: # hsv
                r_f, g_f, b_f = colorsys.hsv_to_rgb(val1, val2, val3)
                r = int(round(r_f * 255))
                g = int(round(g_f * 255))
                b = int(round(b_f * 255))
            country_colors[tag] = [r, g, b]
        return country_colors
    vanilla_colors = parse_colors_file(vanilla_path)
    mod_colors = parse_colors_file(mod_path)
    merged = {}
    for tag in set(list(vanilla_colors.keys()) + list(mod_colors.keys())):
        merged[tag] = mod_colors.get(tag, vanilla_colors.get(tag))
        
    # Fallback to parse individual country files
    mod_common = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common"
    vanilla_common = r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\common"
    tag_to_file = {}
    for base in [vanilla_common, mod_common]:
        tags_dir = os.path.join(base, "country_tags")
        if os.path.exists(tags_dir):
            for f in os.listdir(tags_dir):
                if f.endswith('.txt'):
                    with open(os.path.join(tags_dir, f), 'r', encoding='utf-8', errors='ignore') as file:
                        for line in file:
                            m = re.match(r'^\s*([A-Z0-9]{3})\s*=\s*\"(.*?)\"', line)
                            if m:
                                tag_to_file[m.group(1).upper()] = m.group(2)
                                
    for tag, rel_path in tag_to_file.items():
        if tag not in merged:
            for base in [mod_common, vanilla_common]:
                path = os.path.join(base, rel_path.replace('/', '\\'))
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        m = re.search(r'color\s*=\s*(?:rgb\s*)?\{\s*(\d+)\s+(\d+)\s+(\d+)\s*\}', content)
                        if m:
                            merged[tag] = [int(m.group(1)), int(m.group(2)), int(m.group(3))]
                            break
    return merged


def main():
    print("Loading valid country tags and metadata...")
    valid_tags = parse_valid_tags()
    names = parse_localisation(valid_tags)
    colors = parse_colors()
    
    # Exclude water provinces & load coordinates
    water_provs = set()
    prov_coords = {}
    if os.path.exists("provinces_meta.json"):
        with open("provinces_meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        for pid_str, center_data in meta.get("centers", {}).items():
            pid = int(pid_str)
            if center_data.get("is_water") or center_data.get("is_lake"):
                water_provs.add(pid)
            else:
                prov_coords[pid] = (float(center_data["x"]), float(center_data["y"]))
    print(f"Loaded {len(water_provs)} water provinces to exclude and {len(prov_coords)} land province coordinates.")

    # Get active 2024 tags by simulating the focus tree setup first
    from parse_mod_data_2024 import parse_base_states, parse_2024_transfers
    state_owners, state_cores, state_claims, state_provinces = parse_base_states()
    current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)
    active_2024_tags = set(current_owners.values())
    if 'EUR' in active_2024_tags:
        active_2024_tags.remove('EUR')
    print(f"Restricting color matching to {len(active_2024_tags)} active 2024 country tags.")

    # Calculate geographic centroids for each country tag from its 2024 states
    country_centroids = {}
    for sid, owner in current_owners.items():
        pids = state_provinces.get(sid, [])
        for pid in pids:
            if pid in prov_coords:
                country_centroids.setdefault(owner, []).append(prov_coords[pid])
    
    for tag, coords in list(country_centroids.items()):
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        country_centroids[tag] = (np.mean(xs), np.mean(ys))
    print(f"Calculated centroids for {len(country_centroids)} countries.")

    home_centroids = {
        # South America
        "VEN": (1450.0, 1150.0),
        "BRA": (1600.0, 1350.0),
        "ARG": (1500.0, 1600.0),
        "CHL": (1400.0, 1600.0),
        "COL": (1400.0, 1150.0),
        "PRU": (1400.0, 1300.0),
        "BOL": (1480.0, 1350.0),
        "PAR": (1550.0, 1450.0),
        "URY": (1600.0, 1550.0),
        "ECU": (1350.0, 1200.0),
        "SUR": (1480.0, 1150.0),
        "GUY": (1490.0, 1130.0),
        
        # North America & Caribbean
        "USA": (1100.0, 950.0),
        "CAN": (1000.0, 600.0),
        "MEX": (1150.0, 1100.0),
        "CUB": (1300.0, 1050.0),
        "DOM": (1350.0, 1050.0),
        "HAI": (1330.0, 1050.0),
        "GUA": (1200.0, 1130.0),
        "HON": (1220.0, 1130.0),
        "NIC": (1230.0, 1150.0),
        "CRC": (1250.0, 1170.0),
        "PAN": (1280.0, 1190.0),
        "ELS": (1210.0, 1140.0),
        
        # Oceania
        "AST": (4400.0, 2000.0),
        "NZL": (4900.0, 2200.0),
        "PNG": (4400.0, 1500.0),
        
        # East Asia
        "PRC": (3600.0, 1000.0),
        "CHI": (3600.0, 1000.0),
        "MON": (3600.0, 880.0),
        "JAP": (4100.0, 1000.0),
        "ROK": (4000.0, 950.0),
        "PRK": (4000.0, 920.0),
        
        # South Asia
        "IND": (3200.0, 1150.0),
        "SRL": (3280.0, 1350.0),
        "PAK": (3150.0, 1100.0),
        "BAN": (3300.0, 1150.0),
        "NPL": (3220.0, 1100.0),
        "BHU": (3260.0, 1100.0),
        
        # Southeast Asia
        "BRM": (3480.0, 1180.0),
        "BEI": (3700.0, 1400.0),
        "IDS": (3700.0, 1500.0),
        "PHI": (3900.0, 1250.0),
        "MAL": (3650.0, 1400.0),
        "SIA": (3550.0, 1250.0),
        "VIN": (3600.0, 1200.0),
        "LAO": (3580.0, 1180.0),
        "CAM": (3590.0, 1220.0),
        
        # Europe
        "ROM": (3020.0, 780.0),
        "CZC": (2910.0, 760.0),
        "SLO": (2940.0, 770.0),
        "ITA": (2800.0, 800.0),
        "FRA": (2750.0, 750.0),
        "GER": (2850.0, 720.0),
        "POL": (2950.0, 700.0),
        "UKR": (3100.0, 750.0),
        "BLR": (3100.0, 680.0),
        "SWE": (2900.0, 500.0),
        "NOR": (2800.0, 500.0),
        "FIN": (3000.0, 550.0),
        "ENG": (2700.0, 700.0),
        "POR": (2550.0, 830.0),
        "SPR": (2600.0, 820.0),
        "GRE": (2950.0, 850.0),
        "SWI": (2780.0, 780.0),
        "AUS": (2850.0, 770.0),
        "BEL": (2780.0, 740.0),
        "HOL": (2780.0, 720.0),
        "DEN": (2850.0, 650.0),
        "HUN": (2950.0, 780.0),
        "BUL": (3000.0, 820.0),
        "BOS": (2910.0, 810.0),
        "CRO": (2880.0, 800.0),
        "SER": (2930.0, 820.0),
        "SLV": (2860.0, 790.0),
        "MNT": (2910.0, 830.0),
        "MAC": (2930.0, 840.0),
        "ALB": (2920.0, 840.0),
        "IRE": (2600.0, 680.0),
        "ISL": (2500.0, 450.0),
        
        # Middle East & Central Asia
        "JOR": (2980.0, 1080.0),
        "SAU": (3100.0, 1200.0),
        "TUR": (3000.0, 900.0),
        "AZR": (3200.0, 900.0),
        "PER": (3250.0, 1050.0),
        "IRQ": (3100.0, 1050.0),
        "YEM": (3150.0, 1300.0),
        "OMA": (3220.0, 1250.0),
        "SYR": (3050.0, 1050.0),
        "LEB": (3020.0, 1070.0),
        "ISR": (3000.0, 1090.0),
        "KAZ": (3300.0, 750.0),
        "UZB": (3300.0, 850.0),
        "TKM": (3250.0, 900.0),
        "KGZ": (3400.0, 850.0),
        "TJK": (3400.0, 900.0),
        "AFG": (3200.0, 1050.0),
        "GEO": (3150.0, 880.0),
        "ARM": (3180.0, 900.0),
        
        # Russia
        "RUS": (3300.0, 600.0),
        
        # Africa
        "MOR": (2450.0, 1050.0),
        "TZN": (3150.0, 1450.0),
        "CHA": (2850.0, 1200.0),
        "AZW": (2550.0, 1180.0),
        "LBA": (2800.0, 1100.0),
        "SUD": (3100.0, 1150.0),
        "EGY": (3050.0, 1000.0),
        "KEN": (3180.0, 1380.0),
        "SOM": (3350.0, 1250.0),
        "ETH": (3200.0, 1300.0),
        "SAF": (3050.0, 1750.0),
        "ALG": (2650.0, 1050.0),
        "TUN": (2750.0, 1000.0),
        "NGA": (2800.0, 1300.0),
        "MAD": (3250.0, 1600.0),
        "ANG": (2850.0, 1500.0),
        "MOZ": (3150.0, 1600.0),
        "ZAM": (3000.0, 1500.0),
        "ZIM": (3050.0, 1600.0),
        "NAM": (2900.0, 1650.0),
        "BOT": (2980.0, 1650.0),
        "COD": (2900.0, 1400.0),
        "COG": (2800.0, 1380.0),
        "GAB": (2750.0, 1350.0),
        "CMR": (2800.0, 1280.0),
        "CAR": (2900.0, 1250.0),
        "SSD": (3050.0, 1250.0),
        "UGA": (3120.0, 1350.0),
        "RWA": (3100.0, 1380.0),
        "BDI": (3100.0, 1390.0),
        "MLI": (2550.0, 1180.0),
        "SEN": (2450.0, 1180.0),
        "SLE": (2450.0, 1230.0),
        "LBR": (2480.0, 1250.0),
        "IVC": (2550.0, 1250.0),
        "GHA": (2600.0, 1250.0),
        "TOG": (2620.0, 1250.0),
        "DAH": (2640.0, 1250.0),
        "NGR": (2650.0, 1150.0),
        "BUR": (2580.0, 1180.0),
    }
    print(f"Loaded {len(home_centroids)} manual country centroids for collision resolution.")

    index_path = "provinces_index.png"
    un_map_path = r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png"
    
    print("Loading image arrays...")
    idx_img = Image.open(index_path).convert("RGB")
    un_img = Image.open(un_map_path).convert("RGB")
    
    idx_arr = np.array(idx_img, dtype=np.uint32)
    un_arr = np.array(un_img, dtype=np.uint8)
    
    # Calculate unique province ID for each pixel
    # ID = R + G * 256 + B * 65536
    prov_ids = idx_arr[:, :, 0] + idx_arr[:, :, 1] * 256 + idx_arr[:, :, 2] * 65536
    
    # Reshape arrays to 1D lists of pixels
    flat_ids = prov_ids.reshape(-1)
    flat_colors = un_arr.reshape(-1, 3)
    
    # Group pixel colors by province ID
    print("Grouping colors by province ID...")
    # Find active unique province IDs
    unique_ids, indices = np.unique(flat_ids, return_inverse=True)
    
    # Sum colors and count for each unique ID
    sums = np.zeros((len(unique_ids), 3), dtype=np.uint64)
    counts = np.zeros(len(unique_ids), dtype=np.uint64)
    
    np.add.at(sums, indices, flat_colors)
    np.add.at(counts, indices, 1)
    
    # Compute average RGB for each province
    avg_colors = (sums / counts[:, np.newaxis]).astype(np.uint8)
    
    # Load UN recognized country tags
    with open("scratch/un_mappings.json", "r", encoding="utf-8") as f:
        un_mappings = json.load(f)
    un_tags = {info["tag"] for info in un_mappings.values() if info["tag"]}
    
    # Pre-build RGB list of valid active countries (restricted to UN tags)
    countries_list = []
    countries_colors = []
    for tag in un_tags:
        if tag in colors:
            countries_list.append(tag)
            countries_colors.append(colors[tag])
            
    countries_colors = np.array(countries_colors, dtype=np.float32)

    
    # Count base states for each tag to use as a tie-breaker for identical colors
    base_state_counts = {}
    for sid, owner in state_owners.items():
        base_state_counts[owner] = base_state_counts.get(owner, 0) + 1
        
    ownership = {}
    used_tags = set()
    
    # Define a background / ocean color to skip
    ocean_color = np.array([38, 50, 68], dtype=np.float32)
    
    print("Mapping average province colors to country tags...")
    for idx_item, pid in enumerate(unique_ids):
        pid = int(pid)
        if pid == 0 or pid in water_provs:
            continue
            
        p_color = avg_colors[idx_item].astype(np.float32)
        
        # If the average color is very close to the ocean color, ignore it
        if np.linalg.norm(p_color - ocean_color) < 20:
            continue
            
        # Find closest country tag by Euclidean distance in RGB color space
        dists = np.linalg.norm(countries_colors - p_color, axis=1)
        min_dist = np.min(dists)
        
        if min_dist < 85.0:
            # Gather all tags within 25.0 RGB distance of the minimum distance
            candidates = []
            p_coord = prov_coords.get(pid)
            for i_tag, dist in enumerate(dists):
                if dist <= min_dist + 25.0:
                    tag = countries_list[i_tag]
                    
                    c_coord = home_centroids.get(tag, country_centroids.get(tag))
                    if p_coord and c_coord:
                        dx = abs(p_coord[0] - c_coord[0])
                        dx = min(dx, 5120.0 - dx) # horizontal map wrapping
                        dy = p_coord[1] - c_coord[1]
                        geo_dist = np.sqrt(dx*dx + dy*dy)
                    else:
                        geo_dist = 99999.0
                        
                    candidates.append((tag, dist, geo_dist))
            
            # Sort: lowest geographic distance first
            candidates.sort(key=lambda x: x[2])
            tag = candidates[0][0]
            
            ownership[str(pid)] = tag
            used_tags.add(tag)

    print(f"Final setup: {len(ownership)} provinces owned by {len(used_tags)} tags.")
    
    output_data = {
        "countries": {},
        "ownership": ownership
    }
    
    for tag in un_tags:
        color = colors.get(tag, [150, 150, 150])
        name = names.get(tag, tag)
        output_data["countries"][tag] = {
            "name": name,
            "color": color
        }

        
    with open("preset_ownership.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    print("Successfully generated preset_ownership.json using image-color matching!")

if __name__ == '__main__':
    main()
