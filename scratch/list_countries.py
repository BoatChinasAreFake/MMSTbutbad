import json

with open("preset_ownership.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for tag, c in list(data.get("countries", {}).items())[:20]:
    print(f"Tag: {tag}, Name: {c.get('name')}")
