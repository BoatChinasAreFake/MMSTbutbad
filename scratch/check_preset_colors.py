import json

d = json.load(open('preset_ownership.json'))
meta = json.load(open('provinces_meta.json'))

test_pids = ['17617', '17740', '17755', '17765']
for pid in test_pids:
    owner = d['ownership'].get(pid, 'NONE')
    country_info = d['countries'].get(owner, {})
    print(f"Province {pid}: owner={owner}, name={country_info.get('name')}, color={country_info.get('color')}")
