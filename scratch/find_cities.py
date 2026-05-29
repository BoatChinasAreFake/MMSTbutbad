import json

d = json.load(open('definitions.json'))
meta = json.load(open('provinces_meta.json'))

for pid_str, info in d.items():
    if any(city in info.get('name', '') for city in ['Paris', 'Berlin', 'London', 'Delhi', 'Beijing', 'Addis Ababa']):
        print(pid_str, info.get('name'), meta['centers'].get(pid_str))
