import json

log_path = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get("step_index") == 5789:
            print("FOUND STEP 5789")
            for i, call in enumerate(data.get("tool_calls", [])):
                print(f"Tool call {i}: {call.get('name')}")
                args = call.get("args", {})
                for k, v in args.items():
                    val_str = str(v)
                    print(f"  Arg {k}: type={type(v)}, len={len(val_str)}, first 100 chars={val_str[:100]}")
