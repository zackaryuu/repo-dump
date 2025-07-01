# Example of how to use PngZip
import os
import shutil
from src.png_zip import PngZip

if os.path.exists("output.png"):
    os.remove("output.png")
os.makedirs("generated", exist_ok=True)

png_zip = PngZip("generated/output.png", "w")
png_zip.add_image("test_data/image1.png", "image1")
png_zip.add_image("test_data/image2.png", "image2")
png_zip.save()

with PngZip("generated/output.png", "r") as png_zip:
    w = png_zip["image1"]
    #w.show()
    png_zip["image3"] = "test_data/image3.jpg"

    #
    png_zip["image3"].save("generated/image3.jpg")
    
    png_zip["x"] = "test_data/image4.jpg"

    png_zip["x"].save("generated/image4.jpg")


os.remove("output.png")
shutil.rmtree("generated")