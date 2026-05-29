import json

log_path = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get("source") == "USER_EXPLICIT":
            content = data.get("content", "")
            if any(w in content.lower() for w in ["screenshot", "map", "2024", "downloads"]):
                print(f"User (step {data.get('step_index')}): {content}")
