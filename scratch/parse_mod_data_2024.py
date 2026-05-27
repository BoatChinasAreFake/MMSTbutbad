import os
import re
import json
import colorsys

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
    return merged

def parse_base_states():
    states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
    state_owners = {}
    state_cores = {}
    state_claims = {}
    state_provinces = {}
    
    if not os.path.exists(states_dir):
        return state_owners, state_cores, state_claims, state_provinces
        
    print("Parsing base states...")
    files = [f for f in os.listdir(states_dir) if f.endswith('.txt')]
    for fname in files:
        fpath = os.path.join(states_dir, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        id_match = re.search(r'id\s*=\s*(\d+)', content)
        if not id_match:
            continue
        sid = int(id_match.group(1))
        
        owner_match = re.search(r'owner\s*=\s*([A-Z0-9]{3})', content, re.IGNORECASE)
        if owner_match:
            state_owners[sid] = owner_match.group(1).upper()
            
        cores = re.findall(r'add_core_of\s*=\s*([A-Z0-9]{3})', content, re.IGNORECASE)
        state_cores[sid] = [c.upper() for c in cores]
        
        claims = re.findall(r'add_claim_by\s*=\s*([A-Z0-9]{3})', content, re.IGNORECASE)
        state_claims[sid] = [c.upper() for c in claims]
        
        prov_match = re.search(r'provinces\s*=\s*\{([^}]+)\}', content, re.DOTALL | re.IGNORECASE)
        if prov_match:
            prov_text = prov_match.group(1)
            prov_ids = [int(p) for p in re.findall(r'\b\d+\b', prov_text)]
            state_provinces[sid] = prov_ids
            
    return state_owners, state_cores, state_claims, state_provinces

def tokenize(text):
    # Strip comments line by line
    clean_lines = []
    for line in text.splitlines():
        idx = line.find('#')
        if idx != -1:
            line = line[:idx]
        clean_lines.append(line)
    clean_text = ' '.join(clean_lines)
    
    # Tokenize words, braces, equals sign
    token_re = re.compile(r'({|}|=|[^=\s{}#]+)')
    return token_re.findall(clean_text)

def parse_to_structures(tokens):
    statements = []
    i = 0
    while i < len(tokens):
        if i + 2 < len(tokens) and tokens[i+1] == '=' and tokens[i+2] == '{':
            # key = { ... }
            key = tokens[i]
            brace_count = 1
            j = i + 3
            while j < len(tokens) and brace_count > 0:
                if tokens[j] == '{':
                    brace_count += 1
                elif tokens[j] == '}':
                    brace_count -= 1
                j += 1
            sub_tokens = tokens[i+3:j-1]
            statements.append((key.lower(), parse_to_structures(sub_tokens), True))
            i = j
        elif i + 1 < len(tokens) and tokens[i+1] == '{':
            # key { ... }
            key = tokens[i]
            brace_count = 1
            j = i + 2
            while j < len(tokens) and brace_count > 0:
                if tokens[j] == '{':
                    brace_count += 1
                elif tokens[j] == '}':
                    brace_count -= 1
                j += 1
            sub_tokens = tokens[i+2:j-1]
            statements.append((key.lower(), parse_to_structures(sub_tokens), True))
            i = j
        elif i + 1 < len(tokens) and tokens[i] == '{':
            # anonymous block { ... }
            brace_count = 1
            j = i + 1
            while j < len(tokens) and brace_count > 0:
                if tokens[j] == '{':
                    brace_count += 1
                elif tokens[j] == '}':
                    brace_count -= 1
                j += 1
            sub_tokens = tokens[i+1:j-1]
            statements.append((None, parse_to_structures(sub_tokens), True))
            i = j
        elif i + 2 < len(tokens) and tokens[i+1] == '=':
            # key = val
            statements.append((tokens[i].lower(), tokens[i+2], False))
            i += 3
        else:
            # single word
            statements.append((None, tokens[i], False))
            i += 1
    return statements

def eval_block_struct(sid, owner, state_cores, state_claims, statements):
    for key, val, is_block in statements:
        if is_block:
            if key == 'or':
                if not eval_block_or_struct(sid, owner, state_cores, state_claims, val):
                    return False
            elif key == 'not':
                if eval_block_struct(sid, owner, state_cores, state_claims, val):
                    return False
            elif key == 'and':
                if not eval_block_struct(sid, owner, state_cores, state_claims, val):
                    return False
            elif key == 'limit':
                if not eval_block_struct(sid, owner, state_cores, state_claims, val):
                    return False
        else:
            if not eval_simple_cond_struct(sid, owner, state_cores, state_claims, key, val):
                return False
    return True

def eval_block_or_struct(sid, owner, state_cores, state_claims, statements):
    if not statements:
        return True
    for key, val, is_block in statements:
        if is_block:
            if key == 'not':
                if not eval_block_struct(sid, owner, state_cores, state_claims, val):
                    return True
            elif key == 'and':
                if eval_block_struct(sid, owner, state_cores, state_claims, val):
                    return True
            elif key == 'or':
                if eval_block_or_struct(sid, owner, state_cores, state_claims, val):
                    return True
        else:
            if eval_simple_cond_struct(sid, owner, state_cores, state_claims, key, val):
                return True
    return False

def eval_simple_cond_struct(sid, owner, state_cores, state_claims, key, val):
    if key is None:
        return True
    val = val.upper()
    if key == 'is_owned_by':
        return owner == val
    elif key == 'is_core_of':
        return val in state_cores.get(sid, [])
    elif key == 'is_claimed_by':
        return val in state_claims.get(sid, [])
    return True

def parse_2024_transfers(state_owners, state_cores, state_claims):
    water_path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\national_focus\water.txt"
    if not os.path.exists(water_path):
        print("Error: water.txt not found.")
        return state_owners
        
    print("Simulating 2024 transfers from water.txt...")
    with open(water_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    start_idx = content.find('id = WTR_2024_start')
    if start_idx == -1:
        print("Error: WTR_2024_start not found in water.txt.")
        return state_owners
        
    reward_start = content.find('completion_reward', start_idx)
    brace_count = 0
    idx = content.find('{', reward_start)
    block_content = ""
    for i in range(idx, len(content)):
        char = content[i]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                block_content = content[idx+1:i]
                break
                
    current_owners = dict(state_owners)
    tokens = tokenize(block_content)
    statements = parse_to_structures(tokens)
    
    def process_effects(stmts):
        for key, val, is_block in stmts:
            if is_block:
                if key == 'every_state':
                    limit_statements = []
                    transfers = []
                    for skey, sval, sis_block in val:
                        if sis_block and skey == 'limit':
                            limit_statements = sval
                        elif sis_block and len(skey) == 3:
                            transfers.append((skey.upper(), sval))
                        elif not sis_block and skey == 'transfer_state_to':
                            transfers.append((sval.upper(), None))
                            
                    for sid in list(current_owners.keys()):
                        owner = current_owners[sid]
                        if not limit_statements or eval_block_struct(sid, owner, state_cores, state_claims, limit_statements):
                            for target_tag, sub_block in transfers:
                                if target_tag == 'EUR':
                                    continue
                                current_owners[sid] = target_tag
                elif len(key) == 3:
                    tag = key.upper()
                    if tag != 'EUR':
                        for skey, sval, sis_block in val:
                            if not sis_block and skey == 'transfer_state':
                                try:
                                    sid = int(sval)
                                    current_owners[sid] = tag
                                except ValueError:
                                    pass
                else:
                    process_effects(val)
                    
    process_effects(statements)
    return current_owners

def main():
    valid_tags = parse_valid_tags()
    names = parse_localisation(valid_tags)
    colors = parse_colors()
    
    water_provs = set()
    if os.path.exists("provinces_meta.json"):
        with open("provinces_meta.json", "r", encoding="utf-8") as f:
            meta = json.load(f)
        for pid_str, center_data in meta.get("centers", {}).items():
            if center_data.get("is_water") or center_data.get("is_lake"):
                water_provs.add(int(pid_str))
    print(f"Loaded {len(water_provs)} water provinces to exclude.")
    
    state_owners, state_cores, state_claims, state_provinces = parse_base_states()
    current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)
    
    ownership = {}
    used_tags = set()
    for sid, owner in current_owners.items():
        provs = state_provinces.get(sid, [])
        for pid in provs:
            if pid in water_provs:
                continue
            ownership[str(pid)] = owner
            used_tags.add(owner)
            
    print(f"Final 2024 setup: {len(ownership)} provinces owned by {len(used_tags)} tags.")
    
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
    print("Successfully generated preset_ownership.json for 2024 Modern Day!")

if __name__ == '__main__':
    main()
