import re

log_file = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

print("Scanning raw transcript.jsonl lines...")

with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "computeSpineForComponent" in line and "ctx.rotate" in line and "drawLabels" in line:
            # Let's find all occurrences of code-like sequences
            # We can use regex to extract everything between function drawLabels(){ and the end of the drawing block
            match = re.search(r'function drawLabels\(\)\{.*?ctx\.restore\(\);\s*\}', line, re.DOTALL)
            if match:
                code = match.group(0)
                # Decode unicode escapes if any
                code = code.encode('utf-8').decode('unicode_escape', errors='ignore')
                
                with open("scratch/recovered_drawLabels.js", "w", encoding="utf-8") as out:
                    out.write(code)
                print(f"Successfully recovered code from line {i}! Length: {len(code)}")
                break
            else:
                # If regex fails, let's write the raw line segment to check it
                idx = line.find("function drawLabels")
                if idx != -1:
                    segment = line[idx:idx+8000]
                    segment = segment.encode('utf-8').decode('unicode_escape', errors='ignore')
                    with open("scratch/recovered_segment.js", "w", encoding="utf-8") as out:
                        out.write(segment)
                    print(f"Regex didn't match, but saved raw segment from line {i} to scratch/recovered_segment.js")
                    break
