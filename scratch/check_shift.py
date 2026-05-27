from PIL import Image

def check_alignment():
    p = Image.open('provinces.png').convert('RGB')
    t = Image.open('terrain.png').convert('RGB')
    
    w, h = p.size
    p_pix = p.load()
    t_pix = t.load()
    
    # We want to check if the coastal boundary in provinces.png matches terrain.png
    # Let's find some coordinates where a land province meets water.
    # We will print the pixels of provinces.png and terrain.png in a 10x10 area around a coordinate
    # e.g., the southern tip of some island, or a specific coordinate.
    # Let's find a coordinate where provinces.png goes from water to land.
    # In definitions.json, let's find a water province and a land province that are neighbors.
    import json
    with open('definitions.json', 'r') as f:
        defs = json.load(f)
        
    color_to_type = {tuple(d['color']): d['type'] for d in defs.values()}
    
    # Let's scan a horizontal line near the middle of the map (y=1280) and print where type changes
    print("Scanning horizontal line at y=1280...")
    transitions = []
    prev_type = None
    for x in range(w):
        c = p_pix[x, 1280]
        t_color = t_pix[x, 1280]
        # Check if t_color is water (blue shades have B > R and B > G)
        is_t_water = t_color[2] > t_color[0] and t_color[2] > t_color[1] and t_color[2] > 100
        p_type = color_to_type.get(c, "unknown")
        
        if p_type != "unknown":
            if prev_type and p_type != prev_type:
                transitions.append((x, prev_type, p_type))
            prev_type = p_type
            
    print("First 5 land/water transitions in provinces.png along y=1280:")
    for x, pt, nt in transitions[:10]:
        # Print a 5-pixel neighborhood of terrain water flags
        t_states = []
        for dx in range(-4, 5):
            tc = t_pix[x + dx, 1280]
            is_tw = tc[2] > tc[0] and tc[2] > tc[1] and tc[2] > 100
            t_states.append("W" if is_tw else "L")
        p_states = []
        for dx in range(-4, 5):
            pc = p_pix[x + dx, 1280]
            ptype = color_to_type.get(pc, "L")
            p_states.append("W" if ptype == "water" else "L")
            
        print(f"At x={x}:")
        print("  provinces:", "".join(p_states))
        print("  terrain:  ", "".join(t_states))

if __name__ == '__main__':
    check_alignment()
