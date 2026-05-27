with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

for tag in ['YMM', 'CNL']:
    idx = 0
    print(f"--- Matches for {tag} ---")
    while True:
        idx = content.find(tag, idx)
        if idx == -1:
            break
        print(content[idx-100:idx+200])
        print("="*40)
        idx += 3
