import json

log_file = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

print("Reading line 1015...")

with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 1015:  # 0-indexed line 1015 is line 1016
            data = json.loads(line)
            with open("scratch/step_1015.json", "w", encoding="utf-8") as out:
                json.dump(data, out, indent=2)
            print("Saved step to scratch/step_1015.json")
            break
