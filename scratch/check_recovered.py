import os

print("Scanning recovered files for drawing along spine...")

for fn in sorted(os.listdir("scratch")):
    if fn.startswith("recovered_def_") and fn.endswith(".js"):
        path = os.path.join("scratch", fn)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "ctx.rotate" in content:
            print(f"File {fn} (length {len(content)}) contains ctx.rotate!")
            # Print the text drawing loop
            idx = content.find("ctx.rotate")
            if idx != -1:
                start = max(0, idx - 1000)
                end = min(len(content), idx + 2000)
                print(f"--- SIPPET FROM {fn} ---")
                print(content[start:end])
                print("--- END SNIPPET ---")
