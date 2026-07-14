import json

log_path = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get("step_index") == 5449:
            print("FOUND STEP 5449")
            for call in data.get("tool_calls", []):
                args = call.get("args", {})
                content = args.get("ReplacementContent", args.get("CodeContent", ""))
                # Let's save this content to a file
                with open("scratch/step_5449_extracted.txt", "w", encoding="utf-8") as out:
                    out.write(content)
                print("Saved step 5449 content, length:", len(content))
                break
