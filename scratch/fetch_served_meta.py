import urllib.request
import json

def check():
    url = "http://localhost:8000/provinces_meta.json"
    try:
        print(f"Fetching {url}...")
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        print("Successfully fetched!")
        
        # Check Lough Neagh
        lough_neagh_key = "28985087"
        if lough_neagh_key in data["centers"]:
            print(f"Lough Neagh center meta: {data['centers'][lough_neagh_key]}")
        else:
            print("Lough Neagh key NOT found in centers!")
            
        # Check number of water provinces in centers
        water_count = sum(1 for k, v in data["centers"].items() if v.get("is_water", False))
        print(f"Number of water provinces in centers: {water_count}")
        for k, v in data["centers"].items():
            if v.get("is_water", False):
                print(f"  Water key: {k}, index: {v['index']}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check()
