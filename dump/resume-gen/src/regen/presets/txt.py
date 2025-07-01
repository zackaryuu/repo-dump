import os
import click
from regen.utils import build_input_md
    
captures = ["output.txt"]

def run(profile, data):
    build_input_md(data)
    click.echo("Input file created: input.md")
    os.system(f'pandoc input.md -o output.txt -f markdown -t plain --template="{os.path.join(profile, "template.txt")}" --wrap=none')
    click.echo("Output file created: output.txt")
