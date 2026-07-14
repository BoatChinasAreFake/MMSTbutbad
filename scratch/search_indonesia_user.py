import json

log_path = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        step = data.get("step_index")
        content = data.get("content", "")
        if "USER_INPUT" in data.get("type", "") or data.get("source") == "USER_EXPLICIT":
            if "indonesia" in content.lower():
                print(f"Step {step}:")
                print(content)
                print("="*60)
