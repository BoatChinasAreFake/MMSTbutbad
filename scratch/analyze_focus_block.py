import re

with open('scratch/focus_block_extracted.txt', 'r', encoding='utf-8') as f:
    block = f.read()

# Let's count how many times transfer_state occurs
transfers = re.findall(r'transfer_state\s*=\s*\S+', block)
transfer_tos = re.findall(r'transfer_state_to\s*=\s*\S+', block)
every_states = re.findall(r'every_state\s*=\s*\{', block)

print("Total transfer_state occurrences:", len(transfers))
print("Total transfer_state_to occurrences:", len(transfer_tos))
print("Total every_state occurrences:", len(every_states))

# Let's print the first 20 occurrences of transfer_state_to
print("\nFirst 20 transfer_state_to:")
for x in transfer_tos[:20]:
    print(" ", x)

# Let's print the first 1000 characters of the block
print("\nFirst 1000 chars of extracted block:")
print(block[:1000])
