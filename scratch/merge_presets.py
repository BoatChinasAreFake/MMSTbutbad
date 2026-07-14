import json

def merge():
    # Load current file
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        current_data = json.load(f)
        
    # Load backup file
    with open('preset_ownership_backup.json', 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
        
    # Copy label properties from backup to current data
    keys_to_copy = ['labelOffset', 'labelXOffset', 'curvatureScale', 'fontSizeScale', 'labelRotation', 'labelStretch']
    
    for tag, backup_country in backup_data['countries'].items():
        if tag in current_data['countries']:
            current_country = current_data['countries'][tag]
            for key in keys_to_copy:
                if key in backup_country:
                    current_country[key] = backup_country[key]
                    
    # Save merged data
    with open('preset_ownership.json', 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=2)
        
    print("Merged backup country configurations successfully!")

if __name__ == '__main__':
    merge()
