import urllib.request

def check():
    url = "http://localhost:8000/index.html"
    try:
        print(f"Fetching {url}...")
        response = urllib.request.urlopen(url)
        content = response.read().decode('utf-8')
        print("Successfully fetched!")
        
        # Search for border colors
        print("Checking for diagnostic border color (1.0, 0.0, 0.0, 1.0):")
        if "1.0, 0.0, 0.0, 1.0" in content:
            print("  FOUND old diagnostic RED border color!")
        else:
            print("  NOT found.")
            
        print("Checking for new faint black border color (0.0, 0.0, 0.0, 0.25):")
        if "0.0, 0.0, 0.0, 0.25" in content:
            print("  FOUND new faint black border color!")
        else:
            print("  NOT found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check()
