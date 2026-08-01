import json

def main():
    # Load preset_ownership.json
    with open('preset_ownership.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Clear spines list for all countries to force clean recalculation
    count = 0
    for tag, c in data['countries'].items():
        if 'spines' in c:
            c['spines'] = []
            count += 1

    print(f"Cleared spines cache for {count} countries to force complete visual recalculation.")

    # Save preset_ownership.json
    with open('preset_ownership.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print("Saved preset_ownership.json successfully.")

if __name__ == '__main__':
    main()
