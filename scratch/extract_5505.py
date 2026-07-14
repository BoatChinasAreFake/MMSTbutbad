import json

log_path = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get("step_index") == 5505:
            for call in data.get("tool_calls", []):
                args = call.get("args", {})
                content = args.get("ReplacementContent", args.get("CodeContent", ""))
                print("Found Step 5505 content! Length:", len(content))
                with open("scratch/step_5505_extracted.txt", "w", encoding="utf-8") as out:
                    out.write(content)
                break
