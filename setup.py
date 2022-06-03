from setuptools import setup, find_packages
from flix-cli.core.__version__ import __core__

setup(
    name="flix-cli",
    version=__core__,
    author="demonkingswarn",
    author_email="demonkingswarn@protonmail.com",
    description="A highly efficient, fast, powerful and light-weight movie streamer for your favorite movie.",
    packages=find_packages(),
    url="https://github.com/demonkingswarn/flix-cli",
    keywords=[
        "stream",
        "movie",
        "twist",
        "gdriveplayer",
        "mpv",
    ],
    install_requires=[
        "anitopy==2.1.0",
        "click==8.0.4",
        "comtypes==1.1.11",
        "cssselect==1.1.0",
        "httpx==0.23.0",
        "lxml==4.8.0",
        "tqdm==4.62.3",
        "pycryptodomex==3.14.1",
        "regex==2022.3.15",
        "yarl==1.7.2",
        "pyyaml==6.0",
    ]
)
