import os
import click
from regen.utils import build_input_md

    
def run(profile, data):
    build_input_md(data)
    click.echo("Input file created: input.md")
    
    os.system(f'pandoc input.md -o output.tex -f markdown -t latex --template="{os.path.join(profile, "template.tex")}"')
    click.echo("Output file created: output.tex")
