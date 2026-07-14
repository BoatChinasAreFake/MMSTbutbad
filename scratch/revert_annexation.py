import json

def revert():
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        active_data = json.load(f)
    with open('preset_ownership_backup.json', 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
        
    active_ownership = active_data['ownership']
    backup_ownership = backup_data['ownership']
    
    revert_tags = {'115', '022', '080', '055'}
    count = 0
    
    for p, active_owner in active_ownership.items():
        if p in backup_ownership:
            old_owner = backup_ownership[p]
            if active_owner == '006' and old_owner in revert_tags:
                active_ownership[p] = old_owner
                count += 1
                
    with open('preset_ownership.json', 'w', encoding='utf-8') as f:
        json.dump(active_data, f, indent=2)
        
    print(f"Successfully reverted ownership for {count} provinces!")

if __name__ == '__main__':
    revert()
