import json

with open("preset_ownership.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for tag, c in data.get("countries", {}).items():
    if "indonesia" in c.get("name", "").lower():
        print(f"Tag: {tag}, Name: {c.get('name')}")
