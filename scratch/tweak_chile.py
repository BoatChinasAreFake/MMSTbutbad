import json

def tweak_chile():
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Chile is country id "056"
    chile = data['countries'].get('056')
    if chile:
        print("Original Chile preset:", chile)
        chile['labelOffset'] = 25  # Shift westwards (into Pacific) away from Argentine border
        chile['fontSizeScale'] = 0.9  # Keep font size legible but fitting
        chile['labelStretch'] = 1.3  # Enable light stretching for the single line
        chile['curvatureScale'] = 0.8  # Soften curvature to match path
        print("Updated Chile preset:", chile)
        
    with open('preset_ownership.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

if __name__ == '__main__':
    tweak_chile()
