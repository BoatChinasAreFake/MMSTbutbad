import json

log_file = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

print("Searching transcript.jsonl for computeSpineForComponent definitions...")

matches = []
with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "computeSpineForComponent" in line:
            # Let's see if we can find a large Javascript definition
            # Let's inspect the JSON data to get the contents
            try:
                data = json.loads(line)
                
                # Check contents of planner response or tool calls
                content = data.get("content", "")
                if "function computeSpineForComponent" in content or "function drawLabels" in content:
                    if len(content) > 3000 and "raw_scan_labels" not in content and "find_bezier_labels" not in content:
                        matches.append((i, "content", content))
                
                for tc in data.get("tool_calls", []):
                    args = tc.get("args", {})
                    if not isinstance(args, dict):
                        continue
                    rep = args.get("ReplacementContent") or args.get("CodeContent") or args.get("TargetContent")
                    if rep and "computeSpineForComponent" in rep and len(rep) > 3000:
                        matches.append((i, tc.get("name"), rep))
            except Exception as e:
                pass

print(f"Found {len(matches)} definitions.")
for idx, (line_num, name, code) in enumerate(matches):
    fn = f"scratch/recovered_def_{idx}.js"
    with open(fn, "w", encoding="utf-8") as out:
        out.write(code)
    print(f"Saved match {idx} from line {line_num} (source: {name}, length: {len(code)}) to {fn}")
