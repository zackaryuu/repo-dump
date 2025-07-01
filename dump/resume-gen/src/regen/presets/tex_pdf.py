
import os
import click
from regen.utils import load_preset

captures = [".*.pdf"]

def run(profile, data):
    click.echo("running tex preset")
    load_preset("tex")(profile, data)

    click.echo("building pdf")
    os.system(f'xelatex -interaction=nonstopmode output.tex -include-directory="{profile}"')
    click.echo("pdf created: output.pdf")

