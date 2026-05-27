from parse_mod_data_2024 import parse_base_states, parse_2024_transfers
import os

state_owners, state_cores, state_claims, state_provinces = parse_base_states()
current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)

fra_states = [sid for sid, owner in current_owners.items() if owner == 'FRA']
print("Total FRA states in 2024:", len(fra_states))

# Find the name of some FRA states by looking at their state files
states_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\states"
files = os.listdir(states_dir)
for sid in fra_states[:20]:
    matched = [f for f in files if f.startswith(f"{sid}-") or f == f"{sid}.txt"]
    if matched:
        with open(os.path.join(states_dir, matched[0]), 'r', errors='ignore') as f:
            content = f.read()
            name_line = [line.strip() for line in content.splitlines() if 'name' in line or 'Corsica' in line]
            print(f"  State {sid}: {matched[0]} -> {name_line}")
