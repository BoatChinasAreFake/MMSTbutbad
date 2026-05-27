import re

with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find every_state blocks
idx = 0
every_state_blocks = []
while True:
    idx = content.find('every_state', idx)
    if idx == -1:
        break
    # Find matching brace
    brace_start = content.find('{', idx)
    brace_count = 0
    end_idx = -1
    for i in range(brace_start, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i
                break
    every_state_blocks.append(content[idx:end_idx+1])
    idx = end_idx + 1

print(f"Parsed {len(every_state_blocks)} every_state blocks.")
print("\nFirst 10 every_state blocks:")
for i, block in enumerate(every_state_blocks[:10], 1):
    print(f"Block {i}:")
    print(block[:300])
    print("="*40)
