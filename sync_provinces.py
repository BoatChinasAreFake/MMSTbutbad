import json
import os
from PIL import Image


def compute_interior_point(coords):
    """Return an (x, y) point (rounded to 0.1) that is inside the province.

    Uses the pixel-average centroid when it already lands on a province pixel
    (fast, and identical to the historical behaviour for well-behaved shapes).
    Otherwise it falls back to the "pole of inaccessibility": the interior pixel
    farthest from the province boundary, which is always inside the shape and
    visually well-centered. This keeps labels and selection markers on the
    province even for non-convex, C-shaped, or map-wrapping provinces.
    """
    n = len(coords)
    sum_x = sum(pt[0] for pt in coords)
    sum_y = sum(pt[1] for pt in coords)
    cx = sum_x / n
    cy = sum_y / n

    pixel_set = set(coords)
    if (int(round(cx)), int(round(cy))) in pixel_set:
        return round(cx, 1), round(cy, 1)

    # Fallback: distance transform over the province's bounding-box mask.
    try:
        import numpy as np
        from scipy.ndimage import distance_transform_edt

        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        min_x, min_y = min(xs), min(ys)
        max_x, max_y = max(xs), max(ys)
        mask = np.zeros((max_y - min_y + 1, max_x - min_x + 1), dtype=bool)
        for (x, y) in coords:
            mask[y - min_y, x - min_x] = True
        dt = distance_transform_edt(mask)
        my, mx = np.unravel_index(int(np.argmax(dt)), dt.shape)
        return round(float(min_x + mx), 1), round(float(min_y + my), 1)
    except Exception:
        # scipy/numpy unavailable: snap the centroid to the nearest province pixel.
        best = min(coords, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
        return round(float(best[0]), 1), round(float(best[1]), 1)


def main():
    image_path = "provinces.png"
    index_path = "provinces_index.png"
    meta_path = "provinces_meta.json"
    
    if not os.path.exists(image_path):
        print(f"Error: Could not find provinces.png in the project directory.")
        return
        
    if not os.path.exists(index_path):
        print(f"Error: Could not find provinces_index.png in the project directory.")
        return
        
    if not os.path.exists(meta_path):
        print(f"Error: Could not find {meta_path}")
        return
        
    print(f"Loading display image: {image_path}...")
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = img.load()
    
    print(f"Loading index image: {index_path}...")
    index_img = Image.open(index_path).convert("RGB")
    index_pixels = index_img.load()
    
    print(f"Loading metadata: {meta_path}...")
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta_data = json.load(f)
        
    definitions = meta_data.get("definitions", {})
    centers = meta_data.get("centers", {})
    neighbors = meta_data.get("neighbors", {})
    
    # Map colors to ID from existing definitions
    existing_colors = {}
    for prov_id, d in definitions.items():
        color_tuple = tuple(d["color"])
        existing_colors[color_tuple] = int(prov_id)
        
    # Determine the starting ID for new provinces
    max_id = 0
    if definitions:
        max_id = max(int(k) for k in definitions.keys())
        
    print("Scanning display image for colors...")
    # Find all coordinates for each color
    color_pixel_coords = {}
    
    for y in range(height):
        for x in range(width):
            color = pixels[x, y]
            # Ignore pure white (background/borders)
            if color == (255, 255, 255):
                continue
            if color not in color_pixel_coords:
                color_pixel_coords[color] = []
            color_pixel_coords[color].append((x, y))
            
    print(f"Found {len(color_pixel_coords)} unique colors in display image.")
    
    new_provinces_added = 0
    next_id = max_id + 1
    
    # For index assignment
    max_index = -1
    for center_data in centers.values():
        max_index = max(max_index, center_data.get("index", -1))
    next_index = max_index + 1
    
    index_modified = False
    
    for color, coords in color_pixel_coords.items():
        prov_id_int = existing_colors.get(color)
        
        # If it's a new color
        if prov_id_int is None:
            new_id = str(next_id)
            print(f"Adding new province ID {new_id} for color {color}...")
            
            # Calculate a center point that is guaranteed to be inside the province.
            # A plain pixel-average centroid falls outside non-convex / C-shaped /
            # wrapping provinces, which misplaces labels and selection markers.
            center_x, center_y = compute_interior_point(coords)
            
            # Add to definitions
            definitions[new_id] = {
                "color": list(color),
                "name": f"Province {new_id}",
                "type": "land",
                "terrain": "plains",
                "detailed_terrain": "flatlands"
            }
            
            # Add to centers
            centers[new_id] = {
                "x": center_x,
                "y": center_y,
                "count": len(coords),
                "index": next_index,
                "is_water": False
            }
            
            # Initialize empty neighbors entry
            neighbors[new_id] = []
            
            prov_id_int = next_id
            
            next_id += 1
            next_index += 1
            new_provinces_added += 1
            
        # Write the ID-encoded color to provinces_index.png for all its pixel coords
        # ID encoding is: R = id % 256, G = (id // 256) % 256, B = (id // 65536) % 256
        r_enc = prov_id_int % 256
        g_enc = (prov_id_int // 256) % 256
        b_enc = (prov_id_int // 65536) % 256
        encoded_color = (r_enc, g_enc, b_enc)
        
        for (x, y) in coords:
            if index_pixels[x, y] != encoded_color:
                index_pixels[x, y] = encoded_color
                index_modified = True
                
    if new_provinces_added > 0:
        meta_data["province_count"] = len(definitions)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta_data, f, indent=2)
            
    if index_modified or new_provinces_added > 0:
        print(f"Saving updated index map: {index_path}...")
        index_img.save(index_path)
        print(f"\nSuccess! Registered {new_provinces_added} new provinces and synchronized the index map.")
    else:
        print("\nNo changes or new provinces detected.")

if __name__ == "__main__":
    main()
