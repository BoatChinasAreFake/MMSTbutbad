import os
import re

mod_colors_path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\countries\colors.txt"
if os.path.exists(mod_colors_path):
    with open(mod_colors_path, 'r', errors='ignore') as f:
        content = f.read()
    
    # Find all tag definitions (e.g., TAG = { ... }) and print any that look like cosmetic tags
    # e.g., FRA_something, PRC_something, AST_something
    tags = re.findall(r'^([A-Z0-9_]{3,15})\s*=\s*\{', content, re.MULTILINE)
    print(f"Total tags in colors.txt: {len(tags)}")
    cosmetic_tags = [t for t in tags if '_' in t]
    print(f"Cosmetic tags in colors.txt (first 50):")
    print(cosmetic_tags[:50])
