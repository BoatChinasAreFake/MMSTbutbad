import os
import re
import json
import colorsys

def parse_valid_tags():
    tags_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\country_tags"
    valid_tags = set()
    if not os.path.exists(tags_dir):
        return valid_tags
    
    print("Parsing country tags from common/country_tags...")
    files = [f for f in os.listdir(tags_dir) if f.endswith('.txt')]
    for fname in files:
        fpath = os.path.join(tags_dir, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = re.match(r'^\s*([A-Z0-9]{3})\s*=', line)
                if match:
                    valid_tags.add(match.group(1).upper())
    print(f"Found {len(valid_tags)} valid tags in mod country_tags.")
    return valid_tags

def parse_localisation(valid_tags):
    loc_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\localisation\english"
    names = {}
    
    if not os.path.exists(loc_dir):
        return names
        
    print("Parsing all localisation files in english directory...")
    # Find all .yml files
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
                                # Prefer exact tag name over ideology name, and neutrality/fascism/democratic etc.
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
    return merged

def parse_states():
    states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
    ownership = {}
    used_tags = set()
    
    if not os.path.exists(states_dir):
        print(f"Error: states directory {states_dir} not found.")
        return ownership, used_tags
        
    print("Parsing states...")
    files = [f for f in os.listdir(states_dir) if f.endswith('.txt')]
    for fname in files:
        fpath = os.path.join(states_dir, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        owner_match = re.search(r'owner\s*=\s*([A-Z0-9]{3})', content, re.IGNORECASE)
        if not owner_match:
            continue
        owner = owner_match.group(1).upper()
        
        prov_match = re.search(r'provinces\s*=\s*\{([^}]+)\}', content, re.DOTALL | re.IGNORECASE)
        if not prov_match:
            continue
            
        prov_text = prov_match.group(1)
        prov_ids = re.findall(r'\b\d+\b', prov_text)
        
        for pid in prov_ids:
            ownership[pid] = owner
            used_tags.add(owner)
            
    print(f"Parsed {len(ownership)} provinces owned by {len(used_tags)} tags.")
    return ownership, used_tags

def main():
    valid_tags = parse_valid_tags()
    names = parse_localisation(valid_tags)
    colors = parse_colors()
    ownership, used_tags = parse_states()
    
    output_data = {
        "countries": {},
        "ownership": ownership
    }
    
    for tag in used_tags:
        color = colors.get(tag, [150, 150, 150])
        name = names.get(tag, tag)
        output_data["countries"][tag] = {
            "name": name,
            "color": color
        }
        
    with open("preset_ownership.json", 'w') as f:
        json.dump(output_data, f, indent=2)
    print("Successfully generated preset_ownership.json directly from mod files!")

if __name__ == '__main__':
    main()
