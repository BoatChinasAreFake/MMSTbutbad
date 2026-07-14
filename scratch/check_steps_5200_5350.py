import json

log_path = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step = data.get("step_index")
        if step > 6200:
            continue
        for call in data.get("tool_calls", []):
            args = call.get("args", {})
            content = args.get("ReplacementContent", args.get("CodeContent", ""))
            if "computeSpineForComponent" in content:
                print(f"Step {step}: tool={call.get('name')}, desc={args.get('Description', '')[:100]}")
