import sys
sys.path.append('scratch')
import json
import numpy as np

# Let's trace the exact candidate matching for a Germany province, say 5971 or another province in Germany
meta = json.load(open('provinces_meta.json'))
d = json.load(open('preset_ownership.json'))

from parse_map_image import parse_valid_tags, parse_localisation, parse_colors
valid_tags = parse_valid_tags()
names = parse_localisation(valid_tags)
colors = parse_colors()

# Apply overrides from parse_map_image.py
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

# Pick a province with color [115, 100, 90]
p_color = np.array([115, 100, 90], dtype=np.float32)
dists = np.linalg.norm(countries_colors - p_color, axis=1)
min_dist = np.min(dists)

print("min_dist for [115, 100, 90]:", min_dist)
candidates = []
for i_tag, dist in enumerate(dists):
    if dist <= min_dist + 0.1:
        candidates.append((countries_list[i_tag], dist))
print("Candidates:", candidates)
