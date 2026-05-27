import json
from parse_mod_data_2024 import parse_base_states, parse_2024_transfers

state_owners, state_cores, state_claims, state_provinces = parse_base_states()
print(f"Total base states loaded: {len(state_owners)}")
# Count owners in base states
from collections import Counter
base_counts = Counter(state_owners.values())
print("Top 10 base state owners:")
for tag, count in base_counts.most_common(10):
    print(f"  {tag}: {count} states")

current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)
post_counts = Counter(current_owners.values())
print("Top 10 post-transfer state owners:")
for tag, count in post_counts.most_common(10):
    print(f"  {tag}: {count} states")

# Let's check some specific states like USA, Russia, Germany
# e.g. state for Paris, London, Moscow, Berlin, Washington
# Paris is state 1? No, Corsica is 1. France capital state is usually 121 (or we can find it)
for sid, owner in list(current_owners.items())[:15]:
    base_o = state_owners[sid]
    post_o = owner
    print(f"State {sid}: base owner = {base_o}, post owner = {post_o}")
