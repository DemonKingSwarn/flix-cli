from setuptools import setup, find_packages
from flix_cli.core.__version__ import __core__

with open("requirements.txt") as requirements_txt:
    requirements = requirements_txt.read().splitlines()


setup(
    name="flix-cli",
    version=__core__,
    author="d3m0n@demonkingswarn",
    author_email="demonkingswarn@protonmail.com",
    description="A high efficient, powerful and fast movie scraper.",
    packages=find_packages(),
    url="https://github.com/demonkingswarn/flix-cli",
    keywords=[
        "stream",
        "imdb",
        "twist",
        "free",
        "movies",
        "flix-cli",
        "movie-streamer",
        "gdriveplayer"
    ],
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        flix-cli=flix_cli.__main__:__flixcli__
    """,
    include_package_data=True,
    )
