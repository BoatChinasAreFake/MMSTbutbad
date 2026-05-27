with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('is_core_of = BRA')
if idx != -1:
    print(content[idx-300:idx+600])
