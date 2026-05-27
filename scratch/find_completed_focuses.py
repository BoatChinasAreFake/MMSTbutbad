import re

with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r'complete_national_focus\s*=\s*\S+', content)
print("Completed focuses:", matches)
