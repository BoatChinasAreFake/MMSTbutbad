import os

d = r'C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi'
matches = []
for r, ds, fs in os.walk(d):
    for f in fs:
        if f.endswith('.txt') or f.endswith('.yml'):
            fpath = os.path.join(r, f)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as file:
                    for i, line in enumerate(file, 1):
                        if 'EUR' in line and not 'EURO' in line and not 'EUR_' in line:
                            # Keep only lines with EUR as a word/tag
                            if any(word in line for word in ['EUR', 'EUR =', 'EUR=']):
                                matches.append((fpath, i, line.strip()))
            except Exception as e:
                pass

print(f"Found {len(matches)} matches:")
for path, line_no, text in matches:
    rel = os.path.relpath(path, d)
    print(f"  {rel}:{line_no}: {text}")
