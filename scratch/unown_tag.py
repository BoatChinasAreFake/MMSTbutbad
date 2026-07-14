import json

def main():
    # Load preset_ownership.json
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find provinces owned by tag "040"
    to_delete = []
    for prov_id, tag in data['ownership'].items():
        if tag == '040':
            to_delete.append(prov_id)

    # Delete them from ownership
    for prov_id in to_delete:
        del data['ownership'][prov_id]

    print(f"Removed {len(to_delete)} provinces from tag 040 (giving them to lack of ownership / water).")

    # Save preset_ownership.json
    with open('preset_ownership.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Saved preset_ownership.json successfully.")

if __name__ == '__main__':
    main()
