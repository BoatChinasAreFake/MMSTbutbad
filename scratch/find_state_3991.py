import os
import re

states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
for f in os.listdir(states_dir):
    if f.endswith('.txt'):
        path = os.path.join(states_dir, f)
        with open(path, 'r', errors='ignore') as file:
            if re.search(r'\b3991\b', file.read()):
                print(f"Found province 3991 in state file: {f}")
                break
else:
    print("Province 3991 not found in any state file.")
