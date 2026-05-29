import json

with open("scratch/step_1015.json", "r", encoding="utf-8") as f:
    data = json.load(f)

tool_calls = data.get("tool_calls", [])
for i, tc in enumerate(tool_calls):
    args = tc.get("args", {})
    chunks_arg = args.get("ReplacementChunks", [])
    
    if isinstance(chunks_arg, str):
        chunks = json.loads(chunks_arg)
    else:
        chunks = chunks_arg
        
    print(f"Number of chunks: {len(chunks)}")
    for j, chunk in enumerate(chunks):
        content = chunk.get("ReplacementContent", "")
        # Only print/save if it contains drawLabels or rotate or computeSpine
        if "function drawLabels" in content or "computeSpine" in content or "rotate" in content:
            fn = f"scratch/chunk_{i}_{j}.js"
            with open(fn, "w", encoding="utf-8") as out:
                out.write(content)
            print(f"Saved chunk {j} containing key text to {fn} (length: {len(content)})")
