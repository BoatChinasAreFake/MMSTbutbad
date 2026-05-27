with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

idx = 0
print("--- Matches for AST ---")
while True:
    idx = content.find('AST', idx)
    if idx == -1:
        break
    print(content[idx-100:idx+200])
    print("="*40)
    idx += 3
