import os
import sys
import platform
import subprocess

import click

from .websites.sflix import Sflix
from .websites.actvid import Actvid

calls = {
    "actvid": [Actvid, "https://www.actvid.com"],
    "sflix": [Sflix, "https://sflix.pro"]
}

if platform.system() == "Windows":
    os.system("color FF")

@click.command()

def main():
    for i in calls.keys():
        print(i)
        name = input("Please enter the movie/series with the provider (ex- sflix): ").lower()

        try:
            provider_data = calls.get(name, calls["sflix"])
            provider = provider_data[0](provider_data[1])
            provider.redo()
        except KeyError:
            print("[!] Unsupported provider")
            exit(2)


if __name__ == "__main__":
    main()
