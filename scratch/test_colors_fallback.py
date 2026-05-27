import os
import re

mod_common = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common"
vanilla_common = r"C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\common"
missing = ["BAH", "BEN", "CVD", "FSM", "KIR", "MLD", "MLT", "NAU", "SAM", "SAO", "SEY", "TUV"]

# 1. Parse tag to file mappings
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

print('Mapped tags count:', len(tag_to_file))

# 2. Parse colors for missing
for tag in missing:
    rel_path = tag_to_file.get(tag)
    if not rel_path:
        print(f"{tag}: No path found")
        continue
    found = False
    for base in [mod_common, vanilla_common]:
        path = os.path.join(base, rel_path.replace('/', '\\'))
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                # look for color = { R G B }
                m = re.search(r'color\s*=\s*(?:rgb\s*)?\{\s*(\d+)\s+(\d+)\s+(\d+)\s*\}', content)
                if m:
                    print(f"{tag}: rgb({m.group(1)}, {m.group(2)}, {m.group(3)}) from {path}")
                    found = True
                    break
    if not found:
        print(f"{tag}: Color not found")
