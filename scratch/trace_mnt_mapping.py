import json
import numpy as np
from PIL import Image

idx = Image.open('provinces_index.png').convert('RGB')
un = Image.open(r'C:\Users\Faaz\Downloads\hoi4_map_ENG_1936_01_01_12_1.png').convert('RGB')
idx_arr = np.array(idx, dtype=np.uint32)
un_arr = np.array(un, dtype=np.uint8)
prov_ids = idx_arr[:,:,0] + idx_arr[:,:,1]*256 + idx_arr[:,:,2]*65536

d = json.load(open('preset_ownership.json'))
matching_pids = []
for pid_str, tag in d['ownership'].items():
    if tag == 'MNT':
        pid = int(pid_str)
        mask = (prov_ids == pid)
        if mask.any():
            avg_col = un_arr[mask][0]
            if np.linalg.norm(avg_col - [115, 100, 90]) < 1.0:
                matching_pids.append(pid)

print("Matching PIDs owned by MNT:", matching_pids[:10])

# Trace the execution for the first matching PID
target_pid = matching_pids[0]
meta = json.load(open('provinces_meta.json'))
p_coord = (meta['centers'][str(target_pid)]['x'], meta['centers'][str(target_pid)]['y'])
print("Province coord:", p_coord)

# Load the centroids from parse_map_image.py
import sys
sys.path.append('scratch')
from parse_map_image import parse_valid_tags, parse_localisation, parse_colors
valid_tags = parse_valid_tags()
names = parse_localisation(valid_tags)
colors = parse_colors()

# Apply overrides
colors["USA"] = [80, 115, 167]
colors["CAN"] = [120, 219, 240]
colors["SOV"] = [125, 13, 24]
colors["FRA"] = [67, 142, 135]
colors["GER"] = [115, 100, 90]
colors["ITA"] = [0, 102, 51]
colors["JAP"] = [178, 113, 99]
colors["CHI"] = [204, 95, 27]
colors["RAJ"] = [233, 155, 81]
colors["MON"] = [204, 204, 0]
colors["GXC"] = [230, 100, 0]
colors["YUN"] = [165, 120, 36]
colors["SHX"] = [178, 34, 59]
colors["SIK"] = [0, 98, 51]
colors["TIB"] = [120, 219, 240]
colors["XSM"] = [109, 211, 147]
colors["SPR"] = [95, 216, 121]
colors["TUR"] = [178, 34, 59]
colors["SAU"] = [210, 150, 0]

un_mappings = json.load(open('scratch/un_mappings.json'))
un_tags = {info["tag"] for info in un_mappings.values() if info["tag"]}
tag_aliases = {
    "CHI": "PRC", "GXC": "PRC", "YUN": "PRC", "XSM": "PRC", "SHX": "PRC", "SIK": "PRC", "TIB": "PRC",
    "RAJ": "IND", "INS": "IDS", "SOV": "RUS", "CZE": "CZC", "YUG": "SER", "TAN": "RUS"
}
allowed_tags = un_tags.union(tag_aliases.keys())

countries_list = []
countries_colors = []
for tag in allowed_tags:
    if tag in colors:
        countries_list.append(tag)
        countries_colors.append(colors[tag])
countries_colors = np.array(countries_colors, dtype=np.float32)

# Calculate centroids
from parse_mod_data_2024 import parse_base_states, parse_2024_transfers
state_owners, state_cores, state_claims, state_provinces = parse_base_states()
current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)
prov_coords = {int(k): (float(v['x']), float(v['y'])) for k, v in meta['centers'].items() if not v.get('is_water')}
country_centroids = {}
for sid, owner in current_owners.items():
    pids = state_provinces.get(sid, [])
    for pid in pids:
        if pid in prov_coords:
            country_centroids.setdefault(owner, []).append(prov_coords[pid])
for tag, coords in list(country_centroids.items()):
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]
    country_centroids[tag] = (np.mean(xs), np.mean(ys))

home_centroids = {
    # Europe
    "ROM": (3020.0, 780.0), "CZC": (2910.0, 760.0), "SLO": (2940.0, 770.0), "ITA": (2800.0, 800.0),
    "FRA": (2750.0, 750.0), "GER": (2850.0, 720.0), "POL": (2950.0, 700.0), "UKR": (3100.0, 750.0),
    "BLR": (3100.0, 680.0), "SWE": (2900.0, 500.0), "NOR": (2800.0, 500.0), "FIN": (3000.0, 550.0),
    "ENG": (2700.0, 700.0), "POR": (2550.0, 830.0), "SPR": (2600.0, 820.0), "GRE": (2950.0, 850.0),
    "SWI": (2780.0, 780.0), "AUS": (2850.0, 770.0), "BEL": (2780.0, 740.0), "HOL": (2780.0, 720.0),
    "DEN": (2850.0, 650.0), "HUN": (2950.0, 780.0), "BUL": (3000.0, 820.0), "BOS": (2910.0, 810.0),
    "CRO": (2880.0, 800.0), "SER": (2930.0, 820.0), "SLV": (2860.0, 790.0), "MNT": (2910.0, 830.0),
    "MAC": (2930.0, 840.0), "ALB": (2920.0, 840.0), "IRE": (2600.0, 680.0), "ISL": (2500.0, 450.0),
    # Africa
    "ETH": (2930.0, 1250.0)
}

dists = np.linalg.norm(countries_colors - p_color, axis=1)
min_dist = np.min(dists)

candidates = []
for i_tag, dist in enumerate(dists):
    if dist <= min_dist + 0.1:
        tag = countries_list[i_tag]
        c_coord = home_centroids.get(tag, country_centroids.get(tag))
        if p_coord and c_coord:
            dx = abs(p_coord[0] - c_coord[0])
            dx = min(dx, 5120.0 - dx)
            dy = p_coord[1] - c_coord[1]
            geo_dist = np.sqrt(dx*dx + dy*dy)
        else:
            geo_dist = 99999.0
        candidates.append((tag, dist, geo_dist, c_coord))

candidates.sort(key=lambda x: x[2])
print("Calculated Candidates sorted by geo_dist:")
for c in candidates:
    print(f"  {c[0]}: color_dist={c[1]}, geo_dist={c[2]}, centroid={c[3]}")
