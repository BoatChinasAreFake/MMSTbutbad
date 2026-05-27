import os

d = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\history\countries"
files = os.listdir(d)
for kw in ["China", "Germany", "Australia", "Morocco", "Czech", "Jordan"]:
    matched = [f for f in files if kw.lower() in f.lower()]
    print(f"--- Matches for {kw} ---")
    for f in matched[:10]:
        print("  ", f)
