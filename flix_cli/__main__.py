import sys
import click

from .core.cli.commands import __flix_cli__, __series__
from .core import __version__

def __tv__(query: str):
    if len(sys.argv) == 2:
        query = input("Search: ")
        if query == "":
            print("ValueError: no query parameter provided")
            exit(0)
    else:
        query = " ".join(sys.argv[2:])
    __series__.get_id(query)

commands = {
    "tv": __tv__(),
    "movie": __flix_cli__.fetch(),
}

@click.group(commands=commands)
@click.version_option(__version__.__core__, "-v")
def __flixcli__():
    pass

if __name__ == "__main__":
    __flixcli__()
