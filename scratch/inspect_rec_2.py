with open(r"C:\Users\Faaz\Documents\GitHub\Mappa Mundi sine Tempore\scratch\recovered_def_2.js", "r", encoding="utf-8") as f:
    lines = f.readlines()
    
# Find lines with computeSpineForComponent
start_idx = -1
for i, line in enumerate(lines):
    if "function computeSpineForComponent" in line:
        start_idx = i
        break

if start_idx != -1:
    print("".join(lines[start_idx:start_idx+350]))
else:
    print("Not found")
