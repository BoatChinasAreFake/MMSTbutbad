import json

log_file = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

print("Searching transcript.jsonl...")

matches = []
with open(log_file, "r", encoding="utf-8") as f:
    for line in f:
        if "function drawLabels" in line:
            try:
                data = json.loads(line)
                content = data.get("content", "")
                
                # Filter out search scripts or helper code
                if "function drawLabels" in content and "find_labels_log.py" not in content and "log_file =" not in content and len(content) > 2000:
                    matches.append(content)
                
                for tc in data.get("tool_calls", []):
                    args = tc.get("args", {})
                    if isinstance(args, dict):
                        for k, v in args.items():
                            if isinstance(v, str) and "function drawLabels" in v and "find_labels_log.py" not in v and "log_file =" not in v and len(v) > 2000:
                                matches.append(v)
            except Exception as e:
                pass

print(f"Found {len(matches)} large matches.")
if matches:
    print("--- LAST MATCH (first 2000 chars) ---")
    print(matches[-1][:2000])
    print("--- END ---")
    
    with open("scratch/found_drawLabels.js", "w", encoding="utf-8") as out:
        out.write(matches[-1])
    print("Saved to scratch/found_drawLabels.js")
