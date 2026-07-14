import json

def analyze():
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    non_default = {}
    for cid, country in data['countries'].items():
        has_changed = (
            country.get('labelOffset', 0) != 0 or
            country.get('labelXOffset', 0) != 0 or
            country.get('curvatureScale', 1) != 1 or
            country.get('fontSizeScale', 1) != 1 or
            country.get('labelRotation', 0) != 0 or
            country.get('labelStretch', 1) != 1
        )
        if has_changed:
            non_default[cid] = country
            
    out_lines = [f"Total non-default country presets: {len(non_default)}\n\n"]
    for cid, v in sorted(non_default.items(), key=lambda x: x[0]):
        out_lines.append(f"ID {cid} ({v['name']}):\n")
        out_lines.append(f"  V-Shift (labelOffset): {v.get('labelOffset', 0)}\n")
        out_lines.append(f"  H-Shift (labelXOffset): {v.get('labelXOffset', 0)}\n")
        out_lines.append(f"  Curvature Scale: {v.get('curvatureScale', 1)}\n")
        out_lines.append(f"  Font Size Scale: {v.get('fontSizeScale', 1)}\n")
        out_lines.append(f"  Rotation: {v.get('labelRotation', 0)}\n")
        out_lines.append(f"  Stretching: {v.get('labelStretch', 1)}\n\n")

    with open('scratch/presets_summary.txt', 'w', encoding='utf-8') as out_f:
        out_f.writelines(out_lines)

if __name__ == '__main__':
    analyze()
