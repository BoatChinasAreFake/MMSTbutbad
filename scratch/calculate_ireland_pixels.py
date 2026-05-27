from PIL import Image

def check():
    img = Image.open('provinces.png')
    pixels = img.convert('RGBA').load()
    width, height = img.size

    # Let's count how many pixels each key has
    counts = {}
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            key = ((r << 24) | (g << 16) | (b << 8) | a) & 0xffffffff
            counts[key] = counts.get(key, 0) + 1

    # Sort by count
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("Top 10 largest provinces:")
    for key, count in sorted_counts[:10]:
        print(f"  Key={key:10d}, Count={count}")

if __name__ == '__main__':
    check()
