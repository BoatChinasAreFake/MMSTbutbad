import json
from PIL import Image
import os

def test_mapping():
    prov_img = Image.open('provinces.png').convert('RGB')
    terr_img = Image.open('terrain.bmp')
    
    width, height = prov_img.size
    prov_pix = prov_img.load()
    terr_pix = terr_img.load()
    palette = terr_img.getpalette()
    
    with open('definitions.json', 'r') as f:
        definitions = json.load(f)
    
    color_to_id = {}
    for id_str, d in definitions.items():
        color_to_id[tuple(d["color"])] = id_str
        
    province_pixels = {}
    for y in range(0, height, 4): # subsample to run quickly
        for x in range(0, width, 4):
            p_color = prov_pix[x, y]
            prov_id = color_to_id.get(p_color)
            if prov_id:
                terr_idx = terr_pix[x, y]
                if prov_id not in province_pixels:
                    province_pixels[prov_id] = {}
                province_pixels[prov_id][terr_idx] = province_pixels[prov_id].get(terr_idx, 0) + 1

    # Print top terrain index for a few provinces to see
    print("Sample provinces terrain indices:")
    for prov_id in sorted(list(province_pixels.keys()), key=lambda x: int(x))[:50]:
        counts = province_pixels[prov_id]
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        prov_name = definitions[prov_id]["name"]
        prov_type = definitions[prov_id]["type"]
        top_idx = sorted_counts[0][0]
        rgb = palette[top_idx*3:top_idx*3+3] if palette else None
        print(f"ID {prov_id} ({prov_name}, Type: {prov_type}): Top Terrain Index {top_idx} RGB {rgb} counts {sorted_counts[:3]}")

if __name__ == '__main__':
    test_mapping()
