import json

log_file = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

print("Searching transcript.jsonl for all drawLabels tool calls...")

with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "drawLabels" in line:
            try:
                data = json.loads(line)
                for tc in data.get("tool_calls", []):
                    name = tc.get("name", "")
                    args = tc.get("args", {})
                    if not isinstance(args, dict):
                        continue
                    
                    print(f"Line {i}: Tool {name}, Args: {list(args.keys())}")
                    # If it's a replacement or write, print a snippet
                    content = args.get("ReplacementContent") or args.get("CodeContent") or args.get("TargetContent")
                    if content:
                        print(f"  Content snippet: {content[:100].replace('\n', ' ')}")
            except Exception as e:
                pass
