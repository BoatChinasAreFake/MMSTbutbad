import os

states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
files = [f for f in os.listdir(states_dir) if f.startswith('1646-') or f == '1646.txt' or f.startswith('1646 ')]
if not files:
    # Try finding it by scanning files for id = 1646
    for f in os.listdir(states_dir):
        if f.endswith('.txt'):
            path = os.path.join(states_dir, f)
            with open(path, 'r', errors='ignore') as file:
                if 'id=1646' in file.read().replace(' ', ''):
                    files = [f]
                    break

if files:
    path = os.path.join(states_dir, files[0])
    with open(path, 'r', errors='ignore') as f:
        print(f.read())
else:
    print("State 1646 not found.")
