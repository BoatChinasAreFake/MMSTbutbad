import json

meta = json.load(open('provinces_meta.json'))
xs = [c['x'] for c in meta['centers'].values() if not c.get('is_water')]
ys = [c['y'] for c in meta['centers'].values() if not c.get('is_water')]
print("Land bounding box:")
print(f"  X: {min(xs)} to {max(xs)}")
print(f"  Y: {min(ys)} to {max(ys)}")

# Let's count how many land provinces are in different x ranges
x_ranges = [
    (0, 1000, "Americas"),
    (1000, 2000, "Americas/Atlantic"),
    (2000, 3000, "Europe/Africa"),
    (3000, 4000, "Asia/Indian Ocean"),
    (4000, 5120, "East Asia/Oceania/Pacific")
]
for start, end, label in x_ranges:
    count = sum(1 for c in meta['centers'].values() if not c.get('is_water') and start <= c['x'] < end)
    print(f"  {label} ({start}-{end}): {count} land provinces")
