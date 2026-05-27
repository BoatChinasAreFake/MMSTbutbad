import re

with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for BRA and ARG
bra_matches = [line.strip() for line in content.splitlines() if 'BRA' in line]
arg_matches = [line.strip() for line in content.splitlines() if 'ARG' in line]

print(f"Total BRA references: {len(bra_matches)}")
for match in bra_matches[:10]:
    print(" ", match)

print(f"Total ARG references: {len(arg_matches)}")
for match in arg_matches[:10]:
    print(" ", match)
