import sys
sys.path.append("scratch")
from resolve_un_countries import parse_valid_tags, parse_localisation, un_countries, aliases, manual_overrides
import re
import json

valid_tags = parse_valid_tags()
names = parse_localisation(valid_tags)
name_to_tag = {name.strip().lower(): tag for tag, name in names.items()}

# Strict match first, then aliases, then partial
mappings = {}
for country in un_countries:
    country_clean = country.strip().lower()
    tag = None
    
    if country in manual_overrides:
        tag = manual_overrides[country]
        
    if not tag:
        tag = name_to_tag.get(country_clean)
        
    if not tag and country in aliases:
        for alias in aliases[country]:
            tag = name_to_tag.get(alias.lower())
            if tag:
                break

                
    if not tag:
        # Strict word matching to avoid false partial substring matches
        for name_clean, t in name_to_tag.items():
            if re.search(r'\b' + re.escape(country_clean) + r'\b', name_clean):
                tag = t
                break
                
    if not tag:
        # Fallback to search inside name
        for name_clean, t in name_to_tag.items():
            if country_clean in name_clean:
                tag = t
                break
                
    mappings[country] = (tag, names.get(tag, "NO NAME") if tag else "NONE")

# Write full mappings to a file for verification
with open("scratch/un_mappings.json", "w", encoding="utf-8") as f:
    json_data = {c: {"tag": info[0], "mod_name": info[1]} for c, info in mappings.items()}
    json.dump(json_data, f, indent=2)

print("Generated scratch/un_mappings.json. Here are some matches:")
for c, info in list(mappings.items()):
    if info[0] is None or info[1] == "NO NAME" or len(info[1]) < 2:
        print(f"  WARNING: {c} -> {info[0]} ({info[1]})")
    else:
        print(f"  {c} -> {info[0]} ({info[1]})")
