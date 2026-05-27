with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find all occurrences of BRA
idx = 0
while True:
    idx = content.find('BRA', idx)
    if idx == -1:
        break
    print(f"Occurrence at {idx}:")
    print(content[idx-100:idx+200])
    print("="*40)
    idx += 3
