import json

log_file = r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\.system_generated\logs\transcript.jsonl"

print("Searching transcript.jsonl content fields with lower threshold...")

with open(log_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "computeSpineForComponent" in line and "ctx.rotate" in line and "drawLabels" in line:
            try:
                data = json.loads(line)
                content = data.get("content", "")
                
                # Exclude python search scripts
                if "extract_complete_js.py" in content or "check_recovered" in content or "find_spine_def" in content or "import json" in content:
                    continue
                
                if len(content) > 3000:
                    print(f"Found match in content on line {i}! Length: {len(content)}")
                    with open("scratch/full_recovered_drawLabels.js", "w", encoding="utf-8") as out:
                        out.write(content)
                    break
            except Exception as e:
                pass
