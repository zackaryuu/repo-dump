import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import click
from png_zip import PngZip

@click.group()
def cli():
    pass

@cli.command()
@click.option("-o", "--output", default="output.png")
def pack(output):
    pngzipfile = PngZip(output)
    for file in os.listdir(os.getcwd()):
        ext = os.path.splitext(file)[1]
        if ext in [".png", ".jpg", ".jpeg", ".svg", ".gif"]:
            pngzipfile.add_image(file, os.path.splitext(file)[0])
        
    pngzipfile.save()


if __name__ == "__main__":
    cli()