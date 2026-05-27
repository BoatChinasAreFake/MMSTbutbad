from PIL import Image

def extract():
    bmp_path = r"C:\Users\Faaz\Documents\Paradox Interactive\Hearts of Iron IV\mod\MappaMundi\map\terrain.bmp"
    img = Image.open(bmp_path)
    palette = img.getpalette()
    
    print("Original palette mapping (1-indexed):")
    # Print the exact colors at indices 1 to 80
    for i in range(1, 81):
        rgb = palette[i*3:i*3+3] if palette else [0,0,0]
        print(f"Index {i}: {rgb}")

if __name__ == '__main__':
    extract()
