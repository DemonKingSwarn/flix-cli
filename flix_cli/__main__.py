import sys
import click

from .core.cli.commands import __flix_cli__, __series__
from .core import __version__

commands = {
    "tv": __series__,
    "movie": __flix_cli__,
}

@click.group(commands=commands)
@click.version_option(__version__.__core__, "-v")
def __flixcli__():
    pass

if __name__ == "__main__":
    __flixcli__()
