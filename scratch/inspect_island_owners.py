import json

with open("provinces_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

centers = meta.get("centers", {})

with open("preset_ownership.json", "r", encoding="utf-8") as f:
    preset = json.load(f)

ownership = {}
for k, v in preset.get("ownership", {}).items():
    ownership[int(k)] = v

# Find owners of provinces at different coordinate ranges
sumatra_owners = {}
java_owners = {}
borneo_owners = {}
celebes_owners = {}

for pid, owner in ownership.items():
    c = centers.get(str(pid))
    if c:
        x, y = c["x"], c["y"]
        if 2300 < x < 2700 and 1000 < y < 1400:
            sumatra_owners[owner] = sumatra_owners.get(owner, 0) + 1
        elif 2600 < x < 3200 and 1300 < y < 1500:
            java_owners[owner] = java_owners.get(owner, 0) + 1
        elif 2800 < x < 3300 and 1000 < y < 1300:
            borneo_owners[owner] = borneo_owners.get(owner, 0) + 1
        elif 3200 < x < 3500 and 1000 < y < 1350:
            celebes_owners[owner] = celebes_owners.get(owner, 0) + 1

print("Sumatra owners (X=2300..2700):", sumatra_owners)
print("Java owners (X=2600..3200):", java_owners)
print("Borneo owners (X=2800..3300):", borneo_owners)
print("Celebes owners (X=3200..3500):", celebes_owners)
