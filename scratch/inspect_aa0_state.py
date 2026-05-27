import os
import re

states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
for f in os.listdir(states_dir):
    if f.endswith('.txt'):
        path = os.path.join(states_dir, f)
        with open(path, 'r', errors='ignore') as file:
            content = file.read()
            if 'owner = AA0' in content or 'owner=AA0' in content:
                print(f"Found AA0 state file: {f}")
                print(content)
                break
else:
    print("No state owned by AA0 found.")
