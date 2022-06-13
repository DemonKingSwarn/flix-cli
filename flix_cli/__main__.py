from .core import __flix_cli__
import sys

def __flixcli__():
    query = "".join(sys.argv[1:])
    __flix_cli__.get_id

if __name__ == "__main__":
    __flixcli__()
