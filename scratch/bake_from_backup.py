import json
import re

def main():
    # 1. Load preset_ownership_backup.json
    with open('preset_ownership_backup.json', 'r', encoding='utf-8') as f:
        backup_data = json.load(f)

    # 2. Extract non-default country presets to bake
    base_presets = {}
    
    for tag, c in backup_data['countries'].items():
        is_non_default = (
            c.get('labelOffset', 0) != 0 or
            c.get('labelXOffset', 0) != 0 or
            c.get('labelArcShift', 0) != 0 or
            c.get('curvatureScale', 1.0) != 1.0 or
            c.get('fontSizeScale', 1.0) != 1.0 or
            c.get('labelRotation', 0) != 0 or
            c.get('labelStretch', 1.0) != 1.0
        )
        if is_non_default:
            base_presets[tag] = {
                'labelOffset': c.get('labelOffset', 0),
                'labelXOffset': c.get('labelXOffset', 0),
                'labelArcShift': c.get('labelArcShift', 0),
                'curvatureScale': c.get('curvatureScale', 1.0),
                'fontSizeScale': c.get('fontSizeScale', 1.0),
                'labelRotation': c.get('labelRotation', 0),
                'labelStretch': c.get('labelStretch', 1.0)
            }

    print(f"Extracted {len(base_presets)} base configurations from backup.")

    # 3. Read index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 4. Insert or replace const BASE_COUNTRY_PRESETS
    presets_js = f"const BASE_COUNTRY_PRESETS = {json.dumps(base_presets, indent=4)};\n\n"
    
    if "const BASE_COUNTRY_PRESETS" in html:
        html = re.sub(r'const BASE_COUNTRY_PRESETS = \{.*?\};\s*', presets_js, html, flags=re.DOTALL)
    else:
        html = html.replace("let countries = {", presets_js + "let countries = {")

    # Write back to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully baked base presets from backup into index.html.")

if __name__ == '__main__':
    main()
