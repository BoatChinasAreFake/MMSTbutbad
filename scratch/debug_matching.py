import json
import numpy as np
from PIL import Image

# Load the maps
idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

idx_arr = np.array(idx_img, dtype=np.uint32)
un_arr = np.array(un_img, dtype=np.uint8)

prov_ids = idx_arr[:, :, 0] + idx_arr[:, :, 1] * 256 + idx_arr[:, :, 2] * 65536

# Let's pick a province in Russia
# Moscow is province 3991 or near Y=700, X=2900
pid = 3991
pid_mask = (prov_ids == pid)
p_color = un_arr[pid_mask].mean(axis=0)
print(f"Province {pid} avg color in image: {p_color}")

# Let's run the candidate selection code for this province
import sys
sys.path.append("scratch")
from parse_map_image import parse_colors, parse_valid_tags, parse_localisation
from parse_mod_data_2024 import parse_base_states, parse_2024_transfers

colors = parse_colors()
valid_tags = parse_valid_tags()
names = parse_localisation(valid_tags)
state_owners, state_cores, state_claims, state_provinces = parse_base_states()
current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)
active_2024_tags = set(current_owners.values())
if 'EUR' in active_2024_tags:
    active_2024_tags.remove('EUR')

countries_list = []
countries_colors = []
for tag in active_2024_tags:
    if tag in colors:
        countries_list.append(tag)
        countries_colors.append(colors[tag])
countries_colors = np.array(countries_colors, dtype=np.float32)

dists = np.linalg.norm(countries_colors - p_color, axis=1)
min_dist = np.min(dists)
print(f"Min distance: {min_dist}")

# Let's see the top 10 closest colors in the database
closest_indices = np.argsort(dists)[:10]
for idx in closest_indices:
    tag = countries_list[idx]
    print(f"  {tag} ({names.get(tag)}): color={colors[tag]}, dist={dists[idx]}")
