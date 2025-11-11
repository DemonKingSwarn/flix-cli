<h1 align="center">
  FLIX-CLI
</h1>

<br>
<h3 align="center">
  A high efficient, powerful and fast movie scraper.
</h3>

<div align="center">
  <br>

  ![Language](https://img.shields.io/badge/-python-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)
  
  <a href="https://github.com/demonkingswarn/flix-cli"><img src="https://img.shields.io/github/stars/demonkingswarn/flix-cli?color=orange&logo=github&style=flat-square " alt="starcount"></a> <a href="https://pypi.org/project/flix-cli/" ><img src="https://img.shields.io/pypi/dm/flix-cli" alt="pypi downloads" /></a>

  <a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>

  <img src="https://img.shields.io/badge/os-linux-brightgreen" alt="OS linux">
  <img src="https://img.shields.io/badge/os-freebsd-brightscreen" alt="OS FreeBSD">
  <img src="https://img.shields.io/badge/os-mac-brightgreen"alt="OS Mac">
  <img src="https://img.shields.io/badge/os-windows-brightgreen" alt="OS Windows">
  <img src="https://img.shields.io/badge/os-android-brightgreen" alt="OS Android">
  <img src="https://img.shields.io/badge/os-ios-brightgreen" alt="OS IOS">
  <br>
</div>

<br>

---

![](./.assets/output.gif)

---

# Overview

- [Installation](#installation)
    1. [PIP Installation](#1-pip-installs-packages-aka-pip-installation)
    2. [AUR (Arch Linux)](#2-aur-arch-linux)
    3. [Homebrew (MacOS)](#3-homebrew-macos)
    4. [Scoop (Windows)](#4-scoop-windows)
    5. [WSL (Alternative Window Installation)](#5-wsl-alternative-windows-installation)
    6. [Source Code Download](#6-source-code-download)
    7. [Android Installation](#7-android-installation)
    8. [iSH Installation (IOS)](#8-ish-installation-ios)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Configuration](#configuration)
- [Support](#support)
- [Provider](#provider)
- [Project Disclaimer](#project-disclaimer)
- [Star History](#star-history)
- [Contributing](#contributing)
- [Honourable Mentions](#honourable-mentions)

# Installation
[![AUR version](https://img.shields.io/aur/version/flix-cli?logo=archlinux&label=AUR)](https://aur.archlinux.org/packages/flix-cli)
[![Scoop bucket](https://img.shields.io/badge/Scoop-flix--cli-blue?logo=windows11)](https://github.com/DemonKingSwarn/flix-cli-bucket/blob/master/bucket/flix-cli.json)
[![Homebrew tap](https://img.shields.io/badge/Homebrew-gamedevCloudy%2Ftools-FBB040?logo=homebrew)](https://github.com/gamedevCloudy/homebrew-tools)


<i>for dependencies <a href="https://github.com/DemonKingSwarn/flix-cli#dependencies">(see below)</a>.</i>

This project can be installed on to your device via different mechanisms, these mechanisms are listed below in the order of ease.

## 1. PIP Installs Packages aka PIP Installation
```sh
pip install flix-cli
```

## 2. AUR (Arch Linux)

```sh
paru -S flix-cli
```

## 3. Homebrew (MacOS)

Make sure [Homebrew](https://brew.sh/) is installed in your system.

```sh
brew tap gamedevCloudy/tools
brew install --cask iina
brew install flix-cli
```

## 4. Scoop (Windows)

Make sure [scoop package manager](https://scoop.sh) is installed in your system.

```ps
scoop bucket add extras
scoop bucket add flix-cli https://github.com/DemonKingSwarn/flix-cli-bucket.git
scoop install flix-cli
```

## 5. WSL (Alternative Windows Installation)

Note that the media player (mpv) will need to be installed on Windows, not WSL.

When installing the media player on Windows, make sure that it is on the Windows Path. An easy way to ensure this is to download the media player with a package manager (on Windows, not WSL) such as scoop.

## 6. Installing from source

First ensure <a href="https://docs.astral.sh/uv/getting-started/installation/">UV is installed</a> (blazingly fast Python package manager written in Rust).

Then run the following command:

```sh
git clone https://github.com/demonkingswarn/flix-cli.git \
&& cd flix-cli \
&& uv sync \
&& uv pip install -e . \
&& cd ..
```

**Alternative with Poetry** (legacy):
```sh
git clone https://github.com/demonkingswarn/flix-cli.git \
&& cd flix-cli \
&& poetry build \
&& pip install -e . \
&& cd ..
```

<b>Additional information</b>: You <b>must</b> have Python installed <b>and</b> in PATH to use this project properly. Your Python executable may be `py` or `python` or `python3`. <b>Only Python 3.11 and higher versions are supported by the project.</b>

## 7. Android Installation
Install termux <a href="https://termux.com">(Guide)</a>
```sh
pkg up -y
pkg install python fzf
pip install flix-cli
echo '#!/data/data/com.termux/files/usr/bin/sh' > $PREFIX/bin/mpv
echo 'am start --user 0 -a android.intent.action.VIEW -d "$1" -n is.xyz.mpv/.MPVActivity &' >> $PREFIX/bin/mpv
chmod +x $PREFIX/bin/mpv
```

For it to be able to stream you need to add referrer in mpv by opening mpv <a href="https://play.google.com/store/apps/details?id=is.xyz.mpv">(playstore version)</a>, going into Settings -> Android -> Edit mpv.conf and adding
```sh
referrer="https://flixhq.to"
```

## 8. iSH Installation (IOS)
Install iSH <a href="https://apps.apple.com/us/app/ish-shell/id1436902243">(Guide)</a>
```sh
apk update
apk add python3
apk add py3-pip
apk add fzf
pip install --upgrade flix-cli
```

**NOTE**: You need VLC on your iPhone/iPad

# Dependencies
- [`mpv`](https://mpv.io) - Video Player
- [`iina`](https://iina.io) - Alternate video player for MacOS
- [`vlc`](https://apps.apple.com/us/app/vlc-media-player/id650377962) - Video Player for iPhone/iPad
- [`ffmpeg`](https://github.com/FFmpeg/FFmpeg) - Download manager
- [`fzf`](https://github.com/junegunn/fzf) - for selection menu

# Usage

```sh
Usage: flix-cli [ARGS]...

Options:
    download    Download your favourite movie by query.
    play        Stream your favourite movie by query.
```

# Configuration

- **Windows**: `%APPDATA%/flix-cli/flix-cli.conf`
- **Linux/MacOS/FreeBSD**: `$HOME/.config/flix-cli/flix-cli.conf`

example config file:

```conf
dl_dir="/home/swarn/dl"
```

# Support
You can contact the developer directly via this <a href="mailto:swarn@demonkingswarn.ml">email</a>. However, the most recommended way is to head to the discord server.

<a href="https://discord.gg/JF85vTkDyC"><img src="https://invidget.switchblade.xyz/JF85vTkDyC"></a>

If you run into issues or want to request a new feature, you are encouraged to make a GitHub issue, won't bite you, trust me.

# Provider
| Website                                      | Available Qualities | Status / Elapsed Time                                                                                    | Content Extension   |
| :------------------------------------------: | :-----------------: | :----:                                                                                                   | :-----------------: |
| [flixhq](https://flixhq.to)                  | 720p, 1080p         | <img height="25" src="https://github.com/DemonKingSwarn/flix-status/raw/master/images/gdriveplayer.jpg"> | MP4                 |

# Project Disclaimer
The disclaimer of the project  can be found <a href="https://github.com/demonkingswarn/flix-cli/blob/master/disclaimer.org">here</a>.


## Star History 

[![Star History Chart](https://api.star-history.com/svg?repos=demonkingswarn/flix-cli&type=date&legend=top-left)](https://www.star-history.com/#demonkingswarn/flix-cli&type=date&legend=top-left)

## Contributing 
Pull requests are welcome and *appreciated*. For major changes, please open an issue first to discuss what you would like to change.

<a href = "https://github.com/demonkingswarn/flix-cli/graphs/contributors">
  <img src = "https://contrib.rocks/image?repo=demonkingswarn/flix-cli"/>
</a>

# Honourable Mentions

- [`animdl`](https://github.com/justfoolingaround/animdl): Ridiculously efficient, fast and light-weight (supports most sources: animixplay, 9anime...) (Python)
- [`ani-cli`](https://github.com/pystardust/ani-cli): A cli tool to browse and play anime. (Shell)
- [`mov-cli`](https://github.com/mov-cli/mov-cli): [WIP] watch movies and webseries from the cli. (Python/Shell)
- [`kami`](https://github.com/mrfluffy-dev/kami): Read light novels and watch anime in your terminal. (Rust)
 
