import json
import re

def main():
    # 1. Load preset_ownership.json
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        preset_data = json.load(f)

    # 2. Extract non-default country presets to bake
    base_presets = {}
    keys = ['labelOffset', 'labelXOffset', 'labelArcShift', 'curvatureScale', 'fontSizeScale', 'labelRotation', 'labelStretch']
    
    for tag, c in preset_data['countries'].items():
        # Check if country has non-default settings
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

    # Print how many we extracted
    print(f"Extracted {len(base_presets)} base country configurations to bake.")

    # 3. Reset all countries in preset_ownership.json to defaults
    for tag, c in preset_data['countries'].items():
        c['labelOffset'] = 0
        c['labelXOffset'] = 0
        c['labelArcShift'] = 0
        c['curvatureScale'] = 1.0
        c['fontSizeScale'] = 1.0
        c['labelRotation'] = 0
        c['labelStretch'] = 1.0

    # Save the reset preset_ownership.json
    with open('preset_ownership.json', 'w', encoding='utf-8') as f:
        json.dump(preset_data, f, indent=2)
    print("Reset all preset_ownership.json country offsets to default successfully.")

    # 4. Read index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 5. Insert const BASE_COUNTRY_PRESETS object in index.html right before "let countries ="
    # If BASE_COUNTRY_PRESETS already exists, we replace it.
    presets_js = f"const BASE_COUNTRY_PRESETS = {json.dumps(base_presets, indent=4)};\n\n"
    
    if "const BASE_COUNTRY_PRESETS" in html:
        # Replace existing one
        html = re.sub(r'const BASE_COUNTRY_PRESETS = \{.*?\};\s*', presets_js, html, flags=re.DOTALL)
    else:
        # Insert before "let countries ="
        html = html.replace("let countries = {", presets_js + "let countries = {")

    # 6. Update the loading block in index.html to read base defaults
    # Let's search for the loader code to replace it precisely
    target_loader = """        for (const tag in presetData.countries) {
            const c = presetData.countries[tag];
            countries[tag] = {
                tag: tag,
                name: c.name,
                color: c.color,
                labelOffset: c.labelOffset || 0,
                labelXOffset: c.labelXOffset || 0,
                curvatureScale: c.curvatureScale !== undefined ? c.curvatureScale : 1.0,
                fontSizeScale: c.fontSizeScale !== undefined ? c.fontSizeScale : 1.0,
                labelRotation: c.labelRotation !== undefined ? c.labelRotation : 0,
                labelStretch: c.labelStretch !== undefined ? c.labelStretch : 1.0,
                provinces: new Set()
            };
            COLORS[tag] = c.color;
        }"""

    replacement_loader = """        for (const tag in presetData.countries) {
            const c = presetData.countries[tag];
            const base = BASE_COUNTRY_PRESETS[tag] || {};
            countries[tag] = {
                tag: tag,
                name: c.name,
                color: c.color,
                labelOffset: c.labelOffset !== undefined ? c.labelOffset : (base.labelOffset || 0),
                labelXOffset: c.labelXOffset !== undefined ? c.labelXOffset : (base.labelXOffset || 0),
                labelArcShift: c.labelArcShift !== undefined ? c.labelArcShift : (base.labelArcShift || 0),
                curvatureScale: c.curvatureScale !== undefined ? c.curvatureScale : (base.curvatureScale !== undefined ? base.curvatureScale : 1.0),
                fontSizeScale: c.fontSizeScale !== undefined ? c.fontSizeScale : (base.fontSizeScale !== undefined ? base.fontSizeScale : 1.0),
                labelRotation: c.labelRotation !== undefined ? c.labelRotation : (base.labelRotation !== undefined ? base.labelRotation : 0),
                labelStretch: c.labelStretch !== undefined ? c.labelStretch : (base.labelStretch !== undefined ? base.labelStretch : 1.0),
                provinces: new Set(),
                spines: c.spines || []
            };
            COLORS[tag] = c.color;
        }"""

    if target_loader in html:
        html = html.replace(target_loader, replacement_loader)
        print("Successfully updated the loading block in index.html to support base presets and labelArcShift.")
    else:
        # Fallback regex-based replace in case formatting varies slightly
        pattern = r'for\s*\(\s*const\s+tag\s+in\s+presetData\.countries\s*\)\s*\{.*?countries\[tag\]\s*=\s*\{.*?\};.*?COLORS\[tag\]\s*=\s*c\.color;.*?\n\s*\}'
        html, count = re.subn(pattern, replacement_loader, html, flags=re.DOTALL)
        if count > 0:
            print("Successfully updated the loading block using regex.")
        else:
            print("WARNING: Could not find country loader block in index.html. Check the file manually.")

    # Write the modified index.html back
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully wrote changes back to index.html.")

if __name__ == '__main__':
    main()
