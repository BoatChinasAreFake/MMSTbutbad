import os

dirs = [
    r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\scratch",
    r"C:\Users\Faaz\Documents\GitHub\Mappa Mundi sine Tempore\scratch"
]

for d in dirs:
    if not os.path.exists(d):
        continue
    for f in os.listdir(d):
        if f.endswith(".js") or f.endswith(".txt") or f.endswith(".py"):
            path = os.path.join(d, f)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                    if "computeSpineForComponent" in content:
                        print(f"File {path}: len={len(content)}")
                        # Print occurrences
                        for line in content.splitlines():
                            if "function computeSpineForComponent" in line or "computeSpineForComponent" in line and "function" in line:
                                print("  ", line)
            except Exception as e:
                pass
