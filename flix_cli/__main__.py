import sys

from .core.cli.commands import __flix_cli__
from .core import __version__


#@click.group(commands=commands)
#@click.version_option(__version__.__core__, "-v")

def __flixcli__():
    __flix_cli__


if __name__ == "__main__":
    __flixcli__()
