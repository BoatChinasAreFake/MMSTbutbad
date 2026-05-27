import json
import numpy as np
from PIL import Image

# Load the maps
idx_img = Image.open("provinces_index.png").convert("RGB")
un_img = Image.open(r"C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png").convert("RGB")

idx_arr = np.array(idx_img, dtype=np.uint32)
un_arr = np.array(un_img, dtype=np.uint8)

prov_ids = idx_arr[:, :, 0] + idx_arr[:, :, 1] * 256 + idx_arr[:, :, 2] * 65536
flat_ids = prov_ids.reshape(-1)
flat_colors = un_arr.reshape(-1, 3)

# Load preset_ownership.json to see what is currently mapped
with open("preset_ownership.json", "r", encoding="utf-8") as f:
    preset = json.load(f)

ownership = preset.get("ownership", {})

# Let's find provinces owned by CZE, MOR, AST, PRC, etc.
# We will get their pixel color coordinates in provinces_index.png and sample their colors in un_arr.
with open("provinces_meta.json", "r", encoding="utf-8") as f:
    meta = json.load(f)

centers = meta.get("centers", {})

countries_to_check = ["CZE", "MOR", "AST", "PRC", "CHI", "EGY", "LBY", "SUD", "SOM", "MNG"]

# Let's map province ID to its mapped country
prov_to_country = ownership

# Group provinces by their mapped country
mapped_groups = {}
for pid_str, tag in prov_to_country.items():
    mapped_groups.setdefault(tag, []).append(int(pid_str))

# Let's find some coordinates for these countries on the map
# We can estimate where they are, or check the pixels of provinces mapped to them
print("Checking mapped countries and their average colors in the image:")
for tag in ["CZE", "MOR", "AST", "EGY", "LBY", "SUD", "SOM", "MNG"]:
    pids = mapped_groups.get(tag, [])
    if not pids:
        print(f"No provinces mapped to {tag}")
        continue
    
    # Calculate the average color of all pixels belonging to these provinces in un_img
    colors_list = []
    for pid in pids[:20]: # check first 20 provinces
        pid_mask = (prov_ids == pid)
        if np.any(pid_mask):
            mean_col = un_arr[pid_mask].mean(axis=0)
            colors_list.append(mean_col)
            
    if colors_list:
        avg_col = np.mean(colors_list, axis=0)
        print(f"Country {tag} (mapped): {len(pids)} provinces, Avg RGB in image: {avg_col}")
