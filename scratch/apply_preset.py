import json
import re
import os
from PIL import Image
import colorsys

STARTING_TAGS = {
    "GER", "ENG", "SOV", "USA", "FRA", "ITA", "JAP", "CHI", "RAJ", "AST", 
    "CAN", "SAF", "NZL", "POL", "CZE", "HUN", "ROM", "YUG", "BUL", "GRE", 
    "TUR", "SPA", "SPR", "POR", "SWE", "NOR", "DEN", "FIN", "LAT", "EST", 
    "LIT", "IRE", "BEL", "HOL", "SWI", "AUS", "MEX", "BRA", "ARG", "CHL", 
    "COL", "PRU", "BOL", "ECU", "VEN", "PRY", "URU", "GUA", "HON", "NIC", 
    "COS", "PAN", "CUB", "DOM", "HAI", "SIA", "AFG", "IRA", "OMN", "YEM", 
    "SAU", "NEP", "BHU", "TIB", "SIK", "XSM", "SHX", "CYN", "YUN", "GXC", 
    "PRC", "MAN", "MEN", "MON", "ETH", "LIB", "INS", "PHI"
}

def parse_colors_txt(filepath):
    country_colors = {}
    
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return country_colors
        
    print(f"Parsing {filepath}...")
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
        
    print(f"Parsed {len(country_colors)} countries from colors.txt.")
    return country_colors

def apply_preset():
    vanilla_colors_path = r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\common\countries\colors.txt"
    mod_colors_path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\countries\colors.txt"
    preset_img_path = r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png"
    prov_img_path = "provinces.png"
    definitions_path = "definitions.json"
    output_path = "preset_ownership.json"
    
    if not os.path.exists(preset_img_path):
        print(f"Error: Preset image {preset_img_path} not found.")
        return
        
    # Parse country tag colors
    vanilla_colors = parse_colors_txt(vanilla_colors_path)
    mod_colors = parse_colors_txt(mod_colors_path)
    
    print("Loading images...")
    prov_img = Image.open(prov_img_path).convert('RGB')
    preset_img = Image.open(preset_img_path)
    
    width, height = prov_img.size
    prov_pix = prov_img.load()
    preset_pix = preset_img.load()
    
    preset_palette = preset_img.getpalette()
    
    print("Loading definitions.json...")
    with open(definitions_path, 'r') as f:
        definitions = json.load(f)
        
    print("Loading provinces_meta.json...")
    with open("provinces_meta.json", 'r') as f:
        meta = json.load(f)
        
    color_to_id = {}
    for id_str, d in definitions.items():
        color_to_id[tuple(d["color"])] = id_str
        
    print("Accumulating pixel colors from preset image for each province...")
    province_colors = {}
    for y in range(height):
        for x in range(width):
            p_color = prov_pix[x, y]
            prov_id = color_to_id.get(p_color)
            if prov_id:
                preset_idx = preset_pix[x, y]
                if preset_palette:
                    pr = preset_palette[preset_idx * 3]
                    pg = preset_palette[preset_idx * 3 + 1]
                    pb = preset_palette[preset_idx * 3 + 2]
                else:
                    pr, pg, pb = 0, 0, 0
                    
                rgb = (pr, pg, pb)
                if prov_id not in province_colors:
                    province_colors[prov_id] = {}
                province_colors[prov_id][rgb] = province_colors[prov_id].get(rgb, 0) + 1
                
    # Map tags to a list of both their vanilla and mod colors to handle mixed preset images
    tag_colors = {}
    for tag in STARTING_TAGS:
        tag_colors[tag] = []
        if tag in vanilla_colors:
            tag_colors[tag].append(vanilla_colors[tag])
        if tag in mod_colors:
            tag_colors[tag].append(mod_colors[tag])
            
    all_tag_colors = {}
    all_tags = set(list(vanilla_colors.keys()) + list(mod_colors.keys()))
    for tag in all_tags:
        all_tag_colors[tag] = []
        if tag in vanilla_colors:
            all_tag_colors[tag].append(vanilla_colors[tag])
        if tag in mod_colors:
            all_tag_colors[tag].append(mod_colors[tag])
            
    preset_ownership = {}
    used_tags = set()
    
    print("Mapping dominant colors to country tags...")
    for prov_id, counts in province_colors.items():
        if definitions.get(prov_id, {}).get("type") == "water":
            continue
            
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        dom_color = sorted_counts[0][0]
        
        # Simple neutral/water/wasteland filter (color exactly ocean blue or black)
        if dom_color == (61, 83, 114) or dom_color == (0, 0, 0):
            continue
            
        # Get coordinates of the province from meta["centers"]
        p_meta = meta["centers"].get(prov_id, {})
        px = p_meta.get("x", 0)
        py = p_meta.get("y", 0)
        
        # Manual overrides for mixed/incorrect preset image colors
        matched_tag = None
        if dom_color == (20, 107, 193):
            if py < 1460: # Germany
                matched_tag = "GER"
            else: # Sweden
                matched_tag = "SWE"
        elif dom_color in {(0, 19, 90), (179, 230, 19), (80, 130, 30)}:
            if py < 1260 and 2680 < px < 2960: # Italy region
                matched_tag = "ITA"
                
        if not matched_tag:
            # Match color against starting tags
            best_start_tag = None
            min_start_diff = 9999
            for tag, colors in tag_colors.items():
                for tc in colors:
                    diff = abs(dom_color[0] - tc[0]) + abs(dom_color[1] - tc[1]) + abs(dom_color[2] - tc[2])
                    if diff < min_start_diff:
                        min_start_diff = diff
                        best_start_tag = tag
                        
            if min_start_diff < 60:
                matched_tag = best_start_tag
            else:
                # Try all tags
                best_all_tag = None
                min_all_diff = 9999
                for tag, colors in all_tag_colors.items():
                    for tc in colors:
                        diff = abs(dom_color[0] - tc[0]) + abs(dom_color[1] - tc[1]) + abs(dom_color[2] - tc[2])
                        if diff < min_all_diff:
                            min_all_diff = diff
                            best_all_tag = tag
                if min_all_diff < 60:
                    matched_tag = best_all_tag
                
        if matched_tag:
            preset_ownership[prov_id] = matched_tag
            used_tags.add(matched_tag)
            
    print(f"Assigned {len(preset_ownership)} provinces to {len(used_tags)} unique countries.")
    
    # Save the output preset_ownership.json using mod colors (fallback to vanilla)
    output_data = {
        "countries": {
            tag: {
                "name": tag,
                "color": mod_colors.get(tag, vanilla_colors.get(tag, [150, 150, 150]))
            }
            for tag in used_tags
        },
        "ownership": preset_ownership
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Saved preset ownership to {output_path}.")

if __name__ == '__main__':
    apply_preset()
