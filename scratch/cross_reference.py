import json
import os
import sys
sys.path.append("scratch")
from resolve_un_countries import un_countries

# Load preset ownership
with open("preset_ownership.json", "r", encoding="utf-8") as f:
    preset = json.load(f)

preset_tags = set(preset["countries"].keys())

# Load resolved un mappings (after manually mapping Dominican Republic to DOM)
with open("scratch/un_mappings.json", "r", encoding="utf-8") as f:
    un_mappings = json.load(f)

# Manually ensure Dominican Republic resolves to DOM
if "Dominican Republic" in un_mappings:
    un_mappings["Dominican Republic"]["tag"] = "DOM"
    un_mappings["Dominican Republic"]["mod_name"] = "Dominica" # Or "Dominican Republic"

missing_from_preset = []
mapped_tags = set()

print("Cross-referencing UN countries with preset_ownership.json:")
for cname in un_countries:
    info = un_mappings.get(cname, {})
    tag = info.get("tag")
    if tag:
        mapped_tags.add(tag)
        if tag not in preset_tags:
            missing_from_preset.append((cname, tag))
    else:
        print(f"WARNING: UN country '{cname}' does not map to a tag!")

print(f"\nTotal UN countries/observers: {len(un_countries)}")
print(f"Total preset tags: {len(preset_tags)}")
print(f"Total missing from preset ownership: {len(missing_from_preset)}")
for cname, tag in missing_from_preset:
    print(f"  - {cname} ({tag})")

# Let's check if there are tags in preset that are historical or not UN members/observers
not_un_in_preset = []
for tag in sorted(preset_tags):
    if tag not in mapped_tags:
        not_un_in_preset.append(tag)

print(f"\nPreset tags that are NOT UN recognised members/observers: {len(not_un_in_preset)}")
for tag in not_un_in_preset:
    name = preset["countries"][tag]["name"]
    print(f"  - {tag} ({name})")
