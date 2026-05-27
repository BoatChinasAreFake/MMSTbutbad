import os
import re

path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\countries\cosmetic.txt"
if os.path.exists(path):
    with open(path, 'r', errors='ignore') as f:
        content = f.read()
    
    # Search for cosmetic tags matching _2024
    matches = re.findall(r'([A-Z0-9_]+_2024)\s*=\s*\{[^}]*?color\s*=\s*(rgb|hsv)\s*\{\s*([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s*\}', content, re.DOTALL | re.IGNORECASE)
    print(f"Found {len(matches)} matches:")
    for match in matches:
        print(match)
else:
    print("cosmetic.txt not found")
