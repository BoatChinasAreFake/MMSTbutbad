import json

with open("definitions.json", "r", encoding="utf-8") as f:
    local_defs = json.load(f)

with open("provinces_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

orig_defs = meta.get("definitions", {})

print(f"Original definitions count: {len(orig_defs)}")
print(f"New definitions count: {len(local_defs)}")

diffs = []
for pid, d in local_defs.items():
    orig = orig_defs.get(pid)
    if not orig:
        diffs.append(f"Added province {pid}: {d}")
    else:
        for k, v in d.items():
            if orig.get(k) != v:
                diffs.append(f"Province {pid} [{d.get('name', '')}] changed {k}: {orig.get(k)} -> {v}")

print(f"\nDetected {len(diffs)} changes:")
for change in diffs[:30]:
    print(f"  - {change}")
if len(diffs) > 30:
    print(f"  ... and {len(diffs) - 30} more changes.")
