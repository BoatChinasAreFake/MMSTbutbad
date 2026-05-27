import json
from parse_mod_data_2024 import parse_base_states

state_owners, state_cores, state_claims, state_provinces = parse_base_states()

# Let's count how many provinces are owned by FRA in the base states
fra_provs = []
for sid, owner in state_owners.items():
    if owner == 'FRA':
        fra_provs.extend(state_provinces.get(sid, []))

print("Total base provinces for FRA:", len(fra_provs))
# Print a few of them
print("First 20 FRA province IDs:", fra_provs[:20])

# Let's also check who owns state 121 (usually Paris) in the base states
# We can find state 121 in states dir
import os
import re
states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
for f in os.listdir(states_dir):
    if f.startswith('121-') or f == '121.txt':
        with open(os.path.join(states_dir, f), 'r') as file:
            print("State 121 content:")
            print(file.read()[:300])
