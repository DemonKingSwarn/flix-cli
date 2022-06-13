from setuptools import setup, find_packages

with open("requirements.txt") as requirements_txt:
    requirements = requirements_txt.read().splitlines()

setup(
    name="flix-cli",
    version='0.0.1a',
    author="d3m0n@demonkingswarn",
    author_email="demonkingswarn@protonmail.com",
    description="A module to stream your favorite movies.",
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
        "gdriveplayerr"
    ],
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        flix-cli=flix_cli:__main__.__flix_cli__
    """,
    include_package_data=True,
)
