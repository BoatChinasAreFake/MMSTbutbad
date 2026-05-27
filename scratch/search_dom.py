import os
import re

loc_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\localisation\english"
tags_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\country_tags"

print("Checking country tags for DOM:")
if os.path.exists(tags_dir):
    for f in os.listdir(tags_dir):
        if f.endswith('.txt'):
            path = os.path.join(tags_dir, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                for line in file:
                    if 'DOM' in line or 'DMC' in line:
                        print(f"  {f}: {line.strip()}")

print("\nChecking localisation for 'Dominica':")
if os.path.exists(loc_dir):
    for root, dirs, files in os.walk(loc_dir):
        for f in files:
            if f.endswith('.yml'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8-sig', errors='ignore') as file:
                    for line in file:
                        if 'Dominica' in line or 'DOM_' in line or 'DOM:' in line or 'DMC_' in line or 'DMC:' in line:
                            print(f"  {f}: {line.strip()}")
