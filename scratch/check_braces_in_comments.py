with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('#'):
        if '{' in stripped or '}' in stripped:
            print(f"Line {i}: {stripped}")
