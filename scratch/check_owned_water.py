import json

# Load provinces meta to check which provinces are water
with open('provinces_meta.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)

water_provs = set()
for pid_str, center_data in meta['centers'].items():
    if center_data.get('is_water') or center_data.get('is_lake'):
        water_provs.add(int(pid_str))

print("Total water provinces in meta:", len(water_provs))

# Load preset ownership
with open('preset_ownership.json', 'r', encoding='utf-8') as f:
    preset = json.load(f)

owned_water = {}
for pid_str, tag in preset['ownership'].items():
    pid = int(pid_str)
    if pid in water_provs:
        owned_water[pid] = tag

print("Number of water provinces owned in preset:", len(owned_water))
if owned_water:
    from collections import Counter
    counts = Counter(owned_water.values())
    print("Top owners of water provinces:")
    for tag, count in counts.most_common(10):
        print(f"  {tag}: {count} water provinces")
