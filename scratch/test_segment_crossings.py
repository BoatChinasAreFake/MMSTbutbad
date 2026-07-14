import json

with open("provinces_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

centers = meta.get("centers", {})

with open("preset_ownership.json", "r", encoding="utf-8") as f:
    preset = json.load(f)

ownership = {}
for k, v in preset.get("ownership", {}).items():
    ownership[int(k)] = v

min_x = 9999
max_x = -9999
min_y = 9999
max_y = -9999

indonesia_provs = []
for pid, owner in ownership.items():
    if owner == "011":
        c = centers.get(str(pid))
        if c:
            x, y = c["x"], c["y"]
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            indonesia_provs.append((pid, x, y))

print(f"Indonesia tag 011 bounds: X={min_x}..{max_x}, Y={min_y}..{max_y}")
print(f"First 20 provinces sorted by X:")
indonesia_provs.sort(key=lambda item: item[1])
for p in indonesia_provs[:20]:
    print(f"  ID={p[0]}: x={p[1]}, y={p[2]}")
