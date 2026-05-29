import sys
sys.path.append('scratch')
from parse_mod_data_2024 import parse_base_states
import json

state_owners, state_cores, state_claims, state_provinces = parse_base_states()

from collections import Counter
c = Counter(state_owners.values())
print("State owner counts in mod base states:")
for tag, count in c.most_common(50):
    print(f"  {tag}: {count} states")
