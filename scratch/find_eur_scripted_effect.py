import os

path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\scripted_effects\2024_effect.txt"
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Let's find all occurrences of 'EUR =' or 'EUR=' or similar in the file
idx = 0
while True:
    idx = content.find('EUR', idx)
    if idx == -1:
        break
    # Print the context of the match
    print(f"Occurrence at index {idx}:")
    print(content[idx-100:idx+300])
    print("="*80)
    idx += 3
