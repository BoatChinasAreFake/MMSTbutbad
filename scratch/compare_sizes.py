from PIL import Image

img_uploaded = Image.open(r"C:\Users\Faaz\.gemini\antigravity\brain\1dd19cbb-00fd-498e-94ee-8fb4d2a95dcf\media__1779889930172.png")
print("Uploaded image size:", img_uploaded.size)

img_provs = Image.open("provinces.png")
print("Provinces image size:", img_provs.size)
