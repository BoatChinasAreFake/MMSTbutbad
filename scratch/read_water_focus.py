import sys

water_path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\national_focus\water.txt"
with open(water_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

idx = content.find('id = WTR_2024_start')
if idx == -1:
    print("Not found")
    sys.exit()

# Find the start of the focus = { block
# We search backwards for focus = { or just look for the brace matching the focus = {
# Let's find the focus = { that starts before id = WTR_2024_start
focus_start = content.rfind('focus =', 0, idx)
if focus_start == -1:
    # Maybe it's shared_focus = {
    focus_start = content.rfind('shared_focus =', 0, idx)

if focus_start == -1:
    print("Could not find start of focus block")
    sys.exit()

brace_start = content.find('{', focus_start)
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

print("Total focus block length:", end_idx - focus_start)
with open("scratch/focus_block_extracted.txt", "w", encoding="utf-8") as out:
    out.write(content[focus_start:end_idx+1])
print("Extracted to scratch/focus_block_extracted.txt")
