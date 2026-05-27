import json

def check_neighbors():
    meta = json.load(open('provinces_meta.json'))
    neighbors = meta['neighbors']
    centers = meta['centers']
    
    target_key = "28985087"
    if target_key in neighbors:
        nb = neighbors[target_key]
        print(f"Province {target_key} has neighbors:")
        for n in nb:
            center = centers.get(n, {})
            print(f"  Neighbor {n}: index={center.get('index')}, center=({center.get('x')}, {center.get('y')}), count={center.get('count')}")
    else:
        print(f"Province {target_key} not found in neighbors.")

if __name__ == '__main__':
    check_neighbors()
