import subprocess
import re

print("Running git show HEAD:index.html...")
res = subprocess.run(["git", "show", "HEAD:index.html"], capture_output=True, text=True, encoding="utf-8")
if res.returncode != 0:
    print("Git error:", res.stderr)
else:
    content = res.stdout
    print("HEAD index.html length:", len(content))
    
    # Locate drawLabels
    # Let's find function drawLabels() in the content
    idx = content.find("function drawLabels(){")
    if idx == -1:
        # try search with spaces
        idx = content.find("function drawLabels()")
    
    if idx != -1:
        print("Found drawLabels in HEAD at index", idx)
        # We can extract the function by matching braces or just taking a large chunk
        # Let's find the closing brace by counting nested braces
        braces = 0
        end_idx = -1
        # find the opening brace {
        start_brace = content.find("{", idx)
        if start_brace != -1:
            braces = 1
            for pos in range(start_brace + 1, len(content)):
                if content[pos] == "{":
                    braces += 1
                elif content[pos] == "}":
                    braces -= 1
                    if braces == 0:
                        end_idx = pos
                        break
        
        if end_idx != -1:
            func_code = content[idx:end_idx+1]
            with open("scratch/head_drawLabels.js", "w", encoding="utf-8") as out:
                out.write(func_code)
            print(f"Extracted drawLabels from HEAD! Length: {len(func_code)}")
        else:
            print("Could not find closing brace for drawLabels in HEAD.")
    else:
        print("Could not find drawLabels function in HEAD.")
