import json
import re

log_file = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

print("Searching transcript.jsonl for Bezier/spine label logic...")

matches = []
with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        if "drawLabels" in line:
            try:
                data = json.loads(line)
                # Check contents
                content = data.get("content", "")
                
                # Check if this content contains both computeSpineForComponent and actual drawing along spine
                if "function drawLabels" in content and "computeSpineForComponent" in content and "ctx.rotate" in content and "find_labels_log" not in content:
                    matches.append(content)
                
                for tc in data.get("tool_calls", []):
                    args = tc.get("args", {})
                    if isinstance(args, dict):
                        for k, v in args.items():
                            if isinstance(v, str) and "function drawLabels" in v and "computeSpineForComponent" in v and "ctx.rotate" in v and "find_labels_log" not in v:
                                matches.append(v)
            except Exception as e:
                pass

print(f"Found {len(matches)} matches.")
if matches:
    # Let's save the first one (oldest implementation that had the full rotation/curvature logic)
    with open("scratch/found_spine_drawLabels.js", "w", encoding="utf-8") as out:
        out.write(matches[0])
    print("Saved oldest match to scratch/found_spine_drawLabels.js")
    
    # Let's also save the last one
    with open("scratch/found_spine_drawLabels_last.js", "w", encoding="utf-8") as out:
        out.write(matches[-1])
    print("Saved last match to scratch/found_spine_drawLabels_last.js")
else:
    print("No matches with computeSpineForComponent and ctx.rotate found!")
