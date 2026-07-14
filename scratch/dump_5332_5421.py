import json

log_path = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step = data.get("step_index")
        if step in (5332, 5421):
            print(f"FOUND STEP {step}")
            for call in data.get("tool_calls", []):
                args = call.get("args", {})
                content = args.get("ReplacementContent", args.get("CodeContent", ""))
                # Print first 2000 chars of content (no truncation in print since we can read it)
                print(content[:3000])
                print("="*60)
