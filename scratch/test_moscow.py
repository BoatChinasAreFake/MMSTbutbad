import sys
sys.path.append("scratch")
from parse_map_image import parse_colors, parse_valid_tags, parse_localisation
from parse_mod_data_2024 import parse_base_states, parse_2024_transfers
import os, json
import numpy as np

# Load metadata
valid_tags = parse_valid_tags()
names = parse_localisation(valid_tags)
state_owners, state_cores, state_claims, state_provinces = parse_base_states()
current_owners = parse_2024_transfers(state_owners, state_cores, state_claims)
active_2024_tags = set(current_owners.values())
if 'EUR' in active_2024_tags:
    active_2024_tags.remove('EUR')

colors = parse_colors()

# Manually load the home_centroids from the file
home_centroids = {
    "VEN": (1450.0, 1150.0), "BRA": (1600.0, 1350.0), "ARG": (1500.0, 1600.0),
    "CHL": (1400.0, 1600.0), "COL": (1400.0, 1150.0), "PRU": (1400.0, 1300.0),
    "BOL": (1480.0, 1350.0), "PAR": (1550.0, 1450.0), "URY": (1600.0, 1550.0),
    "ECU": (1350.0, 1200.0), "SUR": (1480.0, 1150.0), "GUY": (1490.0, 1130.0),
    "USA": (1100.0, 950.0), "CAN": (1000.0, 600.0), "MEX": (1150.0, 1100.0),
    "CUB": (1300.0, 1050.0), "DOM": (1350.0, 1050.0), "HAI": (1330.0, 1050.0),
    "GUA": (1200.0, 1130.0), "HON": (1220.0, 1130.0), "NIC": (1230.0, 1150.0),
    "CRC": (1250.0, 1170.0), "PAN": (1280.0, 1190.0), "SLV": (1210.0, 1140.0),
    "AST": (4400.0, 2000.0), "NZL": (4900.0, 2200.0), "PNG": (4400.0, 1500.0),
    "PRC": (3600.0, 1000.0), "CHI": (3600.0, 1000.0), "MON": (3600.0, 880.0),
    "JAP": (4100.0, 1000.0), "ROK": (4000.0, 950.0), "PRK": (4000.0, 920.0),
    "IND": (3200.0, 1150.0), "SRL": (3280.0, 1350.0), "PAK": (3150.0, 1100.0),
    "BAN": (3300.0, 1150.0), "NPL": (3220.0, 1100.0), "BHU": (3260.0, 1100.0),
    "BRM": (3480.0, 1180.0), "BEI": (3700.0, 1400.0), "IDS": (3700.0, 1500.0),
    "PHI": (3900.0, 1250.0), "MAL": (3650.0, 1400.0), "SIA": (3550.0, 1250.0),
    "VIN": (3600.0, 1200.0), "LAO": (3580.0, 1180.0), "CAM": (3590.0, 1220.0),
    "ROM": (3020.0, 780.0), "CZE": (2920.0, 750.0), "ITA": (2800.0, 800.0),
    "FRA": (2750.0, 750.0), "WGR": (2850.0, 720.0), "GER": (2850.0, 720.0),
    "POL": (2950.0, 700.0), "UKR": (3100.0, 750.0), "BLR": (3100.0, 680.0),
    "SWE": (2900.0, 500.0), "NOR": (2800.0, 500.0), "FIN": (3000.0, 550.0),
    "ENG": (2700.0, 700.0), "POR": (2550.0, 830.0), "SPR": (2600.0, 820.0),
    "GRE": (2950.0, 850.0), "SWI": (2780.0, 780.0), "AUS": (2850.0, 770.0),
    "BEL": (2780.0, 740.0), "HOL": (2780.0, 720.0), "DEN": (2850.0, 650.0),
    "HUN": (2950.0, 780.0), "BUL": (3000.0, 820.0), "YUG": (2920.0, 810.0),
    "ALB": (2920.0, 840.0), "IRE": (2600.0, 680.0), "ISL": (2500.0, 450.0),
    "JOR": (2980.0, 1080.0), "SAU": (3100.0, 1200.0), "TUR": (3000.0, 900.0),
    "AZR": (3200.0, 900.0), "PER": (3250.0, 1050.0), "IRQ": (3100.0, 1050.0),
    "YEM": (3150.0, 1300.0), "OMA": (3220.0, 1250.0), "SYR": (3050.0, 1050.0),
    "LEB": (3020.0, 1070.0), "ISR": (3000.0, 1090.0), "KAZ": (3300.0, 750.0),
    "UZB": (3300.0, 850.0), "TKM": (3250.0, 900.0), "KGZ": (3400.0, 850.0),
    "TJK": (3400.0, 900.0), "AFG": (3200.0, 1050.0), "GEO": (3150.0, 880.0),
    "ARM": (3180.0, 900.0), "RUS": (3300.0, 600.0), "MOR": (2450.0, 1050.0),
    "TZN": (3150.0, 1450.0), "CHA": (2850.0, 1200.0), "AZW": (2550.0, 1180.0),
    "LBA": (2800.0, 1100.0), "SUD": (3100.0, 1150.0), "EGY": (3050.0, 1000.0),
    "KEN": (3180.0, 1380.0), "SOM": (3350.0, 1250.0), "ETH": (3200.0, 1300.0),
    "SAF": (3050.0, 1750.0), "ALG": (2650.0, 1050.0), "TUN": (2750.0, 1000.0),
    "NGA": (2800.0, 1300.0), "MAD": (3250.0, 1600.0), "ANG": (2850.0, 1500.0),
    "MOZ": (3150.0, 1600.0), "ZAM": (3000.0, 1500.0), "ZIM": (3050.0, 1600.0),
    "NAM": (2900.0, 1650.0), "BOT": (2980.0, 1650.0), "COD": (2900.0, 1400.0),
    "COG": (2800.0, 1380.0), "GAB": (2750.0, 1350.0), "CMR": (2800.0, 1280.0),
    "CAR": (2900.0, 1250.0), "SSD": (3050.0, 1250.0), "UGA": (3120.0, 1350.0),
    "RWA": (3100.0, 1380.0), "BDI": (3100.0, 1390.0), "MLI": (2550.0, 1180.0),
    "SEN": (2450.0, 1180.0), "SLE": (2450.0, 1230.0), "LBR": (2480.0, 1250.0),
    "IVC": (2550.0, 1250.0), "GHA": (2600.0, 1250.0), "TOG": (2620.0, 1250.0),
    "BEN": (2640.0, 1250.0), "NGR": (2650.0, 1150.0), "BUR": (2580.0, 1180.0),
}

countries_list = []
countries_colors = []
for tag in active_2024_tags:
    if tag in colors and tag in home_centroids:
        countries_list.append(tag)
        countries_colors.append(colors[tag])
countries_colors = np.array(countries_colors, dtype=np.float32)

print(f"Number of active countries compiled: {len(countries_list)}")
print(f"Is 'RUS' in countries_list? {'RUS' in countries_list}")

# Moscow province 2993
pid = 2993
p_color = np.array([0, 127, 13], dtype=np.float32)
p_coord = (3300.0, 500.0)

dists = np.linalg.norm(countries_colors - p_color, axis=1)
min_dist = np.min(dists)
print(f"Min dist: {min_dist}")

candidates = []
for i_tag, dist in enumerate(dists):
    if dist <= min_dist + 25.0:
        tag = countries_list[i_tag]
        c_coord = home_centroids.get(tag)
        dx = abs(p_coord[0] - c_coord[0])
        dx = min(dx, 5120.0 - dx)
        dy = p_coord[1] - c_coord[1]
        geo_dist = np.sqrt(dx*dx + dy*dy)
        candidates.append((tag, dist, geo_dist))

candidates.sort(key=lambda x: x[2])
print("Candidates sorted by geo_dist:")
for item in candidates:
    print(f"  {item[0]}: color_dist={item[1]:.2f}, geo_dist={item[2]:.2f}, centroid={home_centroids.get(item[0])}")
