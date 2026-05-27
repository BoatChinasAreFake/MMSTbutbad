from PIL import Image
import json

def inspect():
    # Load provinces_meta.json
    with open('provinces_meta.json', 'r') as f:
        meta = json.load(f)

    # We want to map each key to its index from meta
    key_to_idx = {}
    for keyStr, data in meta["centers"].items():
        key_to_idx[int(keyStr)] = data["index"]

    img_prov = Image.open('provinces.png')
    pixels_prov = img_prov.convert('RGBA').load()
    
    img_idx = Image.open('provinces_index.png')
    pixels_idx = img_idx.convert('RGBA').load()

    width, height = img_prov.size

    # Let's check a few pixels in the region of Northern Ireland
    # BBox X:[37, 67], Y:[14, 29]
    for y in range(14, 30):
        for x in range(37, 68):
            r, g, b, a = pixels_prov[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            
            # Read index encoded in provinces_index.png
            ri, gi, bi, ai = pixels_idx[x, y]
            idx_encoded = ri + gi * 256 + bi * 65536
            
            idx_expected = key_to_idx.get(key, -1)
            
            if idx_encoded != idx_expected:
                print(f"Mismatch at ({x}, {y}): key={key}, expected_idx={idx_expected}, encoded_idx={idx_encoded}")

    print("Index check complete.")

if __name__ == '__main__':
    inspect()
