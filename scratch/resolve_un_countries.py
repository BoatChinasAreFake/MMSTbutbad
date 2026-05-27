import os
import json
import re

un_countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
    "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
    "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
    "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia",
    "Comoros", "Congo", "Costa Rica", "Cote d'Ivoire", "Croatia", "Cuba", "Cyprus", "Czechia", "North Korea",
    "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt",
    "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France",
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
    "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel",
    "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos",
    "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar",
    "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico",
    "Micronesia", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal",
    "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan",
    "Palau", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar",
    "South Korea", "Moldova", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia",
    "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal",
    "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
    "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria",
    "Tajikistan", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey",
    "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "Tanzania",
    "United States of America", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe",
    # Observers
    "Vatican City", "Palestine"
]

# Aliases to help matching
aliases = {
    "Vatican City": ["VATICAN", "HOLY SEE"],
    "Brunei": ["BRUNEI DARUSSALAM"],
    "Syria": ["SYRIAN ARAB REPUBLIC"],
    "Bolivia": ["BOLIVIA (PLURINATIONAL STATE OF)"],
    "Cote d'Ivoire": ["IVORY COAST", "CÔTE D'IVOIRE"],
    "Iran": ["IRAN (ISLAMIC REPUBLIC OF)", "PERSIA"],
    "Laos": ["LAO PEOPLE'S DEMOCRATIC REPUBLIC"],
    "Micronesia": ["MICRONESIA (FEDERATED STATES OF)"],
    "Myanmar": ["BURMA", "MYANMAR"],
    "North Macedonia": ["MACEDONIA"],
    "Russia": ["RUSSIAN FEDERATION", "SOVIET UNION"],
    "Tanzania": ["UNITED REPUBLIC OF TANZANIA"],
    "Venezuela": ["VENEZUELA (BOLIVARIAN REPUBLIC OF)", "VENEZULA"],
    "Vietnam": ["VIET NAM"],
    "Moldova": ["REPUBLIC OF MOLDOVA"],
    "Siam": ["THAILAND"],
    "Thailand": ["SIAM"],
    "Antigua and Barbuda": ["ANTIGUA-BARBUDA"],
    "Bosnia and Herzegovina": ["BOSNIA"],
    "Burkina Faso": ["UPPER VOLTA"],
    "Cabo Verde": ["CAPE VERDE"],
    "Democratic Republic of the Congo": ["REPUBLIC OF CONGO", "CONGO"],
    "Dominican Republic": ["DOMINICAN"],
    "Eswatini": ["SWAZILAND"],
    "Marshall Islands": ["MARSHALL"],
    "Netherlands": ["HOLLAND"],
    "Saint Kitts and Nevis": ["SAINT KITTS"],
    "Saint Vincent and the Grenadines": ["SAINT VINCENT"],
    "Sao Tome and Principe": ["SAO TOME"],
    "Timor-Leste": ["EAST TIMOR"],
    "Yemen": ["YEMAN"]
}

manual_overrides = {
    "Georgia": "GEO",
    "Dominican Republic": "DOM",
    "Benin": "DAH",
    "Luxembourg": "LUX"
}


def parse_valid_tags():
    tags_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\common\country_tags"
    valid_tags = set()
    if not os.path.exists(tags_dir):
        return valid_tags
    files = [f for f in os.listdir(tags_dir) if f.endswith('.txt')]
    for fname in files:
        fpath = os.path.join(tags_dir, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = re.match(r'^\s*([A-Z0-9]{3})\s*=', line)
                if match:
                    valid_tags.add(match.group(1).upper())
    return valid_tags

def parse_localisation(valid_tags):
    loc_dir = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\localisation\english"
    names = {}
    if not os.path.exists(loc_dir):
        return names
    for root, dirs, files in os.walk(loc_dir):
        for fname in files:
            if not fname.endswith('.yml'):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8-sig', errors='ignore') as f:
                for line in f:
                    match = re.match(r'^\s*([a-z0-9_]+):\d?\s*"(.*?)"', line, re.IGNORECASE)
                    if match:
                        key = match.group(1).upper()
                        name = match.group(2)
                        if key in valid_tags:
                            names[key] = name
                        else:
                            parts = key.split('_')
                            if len(parts) > 1 and parts[0] in valid_tags:
                                tag = parts[0]
                                if tag not in names or key.endswith('_NEUTRALITY') or key.endswith('_FASCISM') or key.endswith('_DEMOCRATIC'):
                                    names[tag] = name
    return names

def main():
    print("Loading valid country tags and names from mod...")
    valid_tags = parse_valid_tags()
    names = parse_localisation(valid_tags)
    print(f"Loaded {len(names)} tags from localisation.")
    
    matched = {}
    unmatched = []
    
    # Inverted name matching
    name_to_tag = {}
    for tag, name in names.items():
        name_clean = name.strip().lower()
        name_to_tag[name_clean] = tag
        
    for country in un_countries:
        country_clean = country.strip().lower()
        tag = None
        
        # 0. Manual overrides
        if country in manual_overrides:
            tag = manual_overrides[country]
            
        # 1. Direct name match
        if not tag:
            tag = name_to_tag.get(country_clean)
        
        # 2. Check aliases
        if not tag and country in aliases:
            for alias in aliases[country]:
                tag = name_to_tag.get(alias.lower())
                if tag:
                    break
                    
        # 3. Partial check
        if not tag:
            for name_clean, t in name_to_tag.items():
                if country_clean in name_clean or name_clean in country_clean:
                    # Let's verify it is a close match
                    tag = t
                    break

                    
        if tag:
            matched[country] = (tag, names[tag])
        else:
            unmatched.append(country)
            
    print(f"\nSuccessfully matched {len(matched)} / {len(un_countries)} countries.")
    print("\nUnmatched Countries:")
    for country in unmatched:
        print(f"  {country}")
        
    print("\nMatched Mapping sample:")
    for c, info in list(matched.items())[:20]:
        print(f"  {c} -> {info[0]} ({info[1]})")

if __name__ == '__main__':
    main()
