import json
from collections import Counter

with open('preset_ownership.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

counts = Counter(data['ownership'].values())
print("Top 30 countries by province counts:")
for tag, count in counts.most_common(30):
    name = data['countries'].get(tag, {}).get('name', tag)
    print(f"  {tag} ({name}): {count} provinces")
