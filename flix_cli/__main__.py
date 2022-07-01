from .core import __flix_cli__
from .core.utils.player import play
from .core.utils.downloader import download

def __flixcli__():
    __flix_cli__.show_info

if __name__ == "__main__":
    __flixcli__()
