<p align="center">
<br>
<a href="https://github.com/demonkingswarn/flix-cli"><img src="https://img.shields.io/github/stars/demonkingswarn/flix-cli?color=orange&logo=github&style=flat-square"></a>
<a href="http://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg"></a>
<img src="https://img.shields.io/badge/os-linux-brightgreen">
<img src="https://img.shields.io/badge/os-mac-brightgreen">
<img src="https://img.shields.io/badge/os-windows-brightgreen">
<img src="https://img.shields.io/badge/os-android-brightgreen">
<br>
</p>
<h1 align="center">
  FLIX-CLI
</h1>
<br>
<h3 align="center">
  A high efficient, powerful and fast movie scraper.
</h3>
<br>
<img src="https://github.com/DemonKingSwarn/flix-cli/raw/master/.assets/showcase.gif">

<hr>

# Installation
<i>for dependencies <a href="https://github.com/DemonKingSwarn/flix-cli#dependencies">(see below)</a>.</i>

This project can be installed on to your device via different mechanisms, these mechanisms are listed below in the order of ease.

## 1. PIP Installs Packages aka PIP Installation
```sh
pip install flix-cli
```

## 2. Source Code Download
``` sh
git clone https://github.com/demonkingswarn/flix-cli
```

Given that you have `git` installed, you can clone the repository from GitHub. If you do not have or want to deal with installation of `git`, you can simply download the repository using <a href="https://github.com/demonkingswarn/flix-cli/archive/refs/heads/master.zip">this link</a>.

<b>Additional information</b>: You <b>must</b> have Python installed <b>and</b> in PATH to use this project properly. Your Python executable may be `py` or `python` or `python3`. <b>Only Python 3.6 and higher versions are supported by the project.</b>

## 3. Android Installation
Install termux <a href="https://termux.com">(Guide)</a>
```sh
pkg up -y
pip install flix-cli
echo "#\!/data/data/com.termux/files/usr/bin/sh" > $PREFIX/bin/mpv
echo 'am start --user 0 -a android.intent.action.VIEW -d "$1" -n is.xyz.mpv/.MPVActivity &' >> $PREFIX/bin/mpv
chmod +x $PREFIX/bin/mpv
```

For it to be able to stream you need to add referrer in mpv by opening mpv <a href="https://play.google.com/store/apps/details?id=is.xyz.mpv">(playstore version)</a>, going into Settings -> Android -> Edit mpv.conf and adding
```sh
referrer="https://membed.net"
```

# Dependencies
- mpv - Video Player
- vlc - Alternate video player
- ffmpeg - Download manager

# Usage

```sh
Usage: flix-cli [ARGS]...

Options:
    download    Download your favourite movie by query.
    play        Stream your favourite movie by query.
```

# Support
You can contact the developer directly via this <a href="mailto:demonkingswarn@protonmail.com">email</a>. However, the most recommended way is to head to the discord server.

<a href="https://discord.gg/JF85vTkDyC"><img src="https://invidget.switchblade.xyz/JF85vTkDyC"></a>

If you run into issues or want to request a new feature, you are encouraged to make a GitHub issue, won't bite you, trust me.

# Provider
| Website                                      | Available Qualities | Status / Elapsed Time | Content Extension |
| :------------------------------------------: | :-----------------:  | :----: | :-----------------: |
| [gdriveplayer](https://database.gdriveplayer.us/player.php)         | 720p, 1080p | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/nineanime.png">  | MP4 |

# Project Disclaimer
The disclaimer of the project  can be found <a href="https://github.com/demonkingswarn/flix-cli/blob/master/disclaimer.org">here</a>.
