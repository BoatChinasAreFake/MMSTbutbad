import os

for fn in sorted(os.listdir("scratch")):
    if fn.startswith("recovered_def_") and fn.endswith(".js"):
        path = os.path.join("scratch", fn)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "truncated" in content:
            print(f"{fn} is truncated")
        else:
            print(f"{fn} is NOT truncated! Length: {len(content)}")
