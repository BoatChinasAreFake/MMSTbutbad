import json

d = json.load(open('preset_ownership.json'))
meta = json.load(open('provinces_meta.json'))

# Let's count the owners of ALL provinces in the India box: 3000 < x < 3500, 1000 < y < 1400
owners = {}
for pid_str, c in meta['centers'].items():
    if not c.get('is_water') and 3000 < c['x'] < 3500 and 1000 < c['y'] < 1400:
        tag = d['ownership'].get(pid_str, 'NONE')
        owners[tag] = owners.get(tag, 0) + 1

print("Owners in India region:")
for tag, count in sorted(owners.items(), key=lambda x: x[1], reverse=True):
    print(f"  {tag}: {count} provinces")
