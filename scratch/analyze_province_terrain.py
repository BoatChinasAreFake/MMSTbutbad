import json
from PIL import Image
from collections import Counter

def analyze():
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
    print("Sampling pixels...")
    for y in range(0, height, 2): # sample every 2nd pixel to be fast and accurate
        for x in range(0, width, 2):
            p_color = prov_pix[x, y]
            prov_id = color_to_id.get(p_color)
            if prov_id:
                terr_idx = terr_pix[x, y]
                if prov_id not in province_pixels:
                    province_pixels[prov_id] = {}
                province_pixels[prov_id][terr_idx] = province_pixels[prov_id].get(terr_idx, 0) + 1

    top_indices = {}
    index_types = Counter()
    for prov_id, counts in province_pixels.items():
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        top_idx = sorted_counts[0][0]
        top_indices[prov_id] = top_idx
        index_types[top_idx] += 1
        
    print("\nTop index distribution among all sampled provinces:")
    for idx, count in index_types.most_common(40):
        rgb = palette[idx*3:idx*3+3] if palette else None
        print(f"Index {idx} RGB {rgb}: {count} provinces")

if __name__ == '__main__':
    analyze()
