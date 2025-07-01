import click
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from regen import EXAMPLE_TOML, PRESETS, PROFILES, PROFILE_PATH
from regen.utils import oprun

@click.command()
@click.option("-s", "--preset", type=click.Choice(PRESETS), default=PRESETS[0])
@click.option("-p", "--profile", type=click.Choice(PROFILES), default=PROFILES[0])
@click.option("-d", "--data", type=click.Path(exists=True), default=None)
@click.option("-e", "--example", is_flag=True, default=False, help="Use example.toml as data file.")
@click.option("-o", "--output", type=click.Path(exists=False, file_okay=False), default=None, help="Output file path.")
def cli(preset, profile, data, example, output):
    click.echo(f"Preset: {preset}")
    click.echo(f"Profile: {profile}")

    # find data.toml in currentCwd, if not find the first .toml 
    if example:
        data_toml = EXAMPLE_TOML
    else:
        data_toml = data
    if data_toml and not data_toml.endswith(".toml"):
        click.echo(f"Data file {data_toml} is not a .toml file, exiting.")
        return
    
    currentCwd = os.path.abspath(os.getcwd())
    click.echo(f"Current working directory: {currentCwd}")

    if data_toml is None:
        data_toml = os.path.join(currentCwd, "data.toml")
        
        if not os.path.exists(data_toml):
            data_toml = next((os.path.join(currentCwd, file) for file in os.listdir(currentCwd) if file.endswith(".toml")), None)

        if data_toml is None:
            click.echo("No data.toml found in current directory, using example.toml.")
            data_toml = EXAMPLE_TOML

    data_toml = os.path.abspath(data_toml)

    click.echo(f"Data file: {data_toml}")

    if output:
        os.makedirs(output, exist_ok=True)
        os.chdir(output)
        currentCwd = os.path.abspath(os.getcwd())

    oprun(preset, currentCwd, os.path.join(PROFILE_PATH, profile), data_toml)

if __name__ == "__main__":
    cli()
