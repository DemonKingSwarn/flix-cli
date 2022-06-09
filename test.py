#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import re
import httpx
import subprocess
import time

def get_tv():
    client = httpx.Client(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'})

    MPV_EXECUTABLE = "mpv"
    DEFAULT_REFFERER = "https://dood.to"
    md5_regex = r"/(pass_md5/.+?)'"

    base_url = "https://allmoviesforyou.net/episode"

    series = input("Search: ")
    series = series.replace(" ", "-")
    season = input("Enter season: ")
    episode = input("Enter episode: ")

    url = f"{base_url}/{series}-{season}x{episode}"

    r=client.get("https://check.ddos-guard.net/check.js").text
    r=client.get(url)
    soup = bs(r.text, "html.parser")
    iframe_link = soup.select("iframe")[0]["src"]

    r=client.get(iframe_link).text
    soup = bs(r, "html.parser")
    dood_link = soup.select("iframe")[0]["src"]

    r=client.get(dood_link)
    hash = re.findall(md5_regex, r.text)[0]
    token = hash.split("/")[-1]

    r=client.get(f"https://dood.to/{hash}",headers={"Referer":"https://dood.to"})

    link = f"{r.text}doodstream?token={token}&expiry={int(time.time() * 1000)}"

    args = [
        MPV_EXECUTABLE,
        f"{link}",
        f"--referrer={DEFAULT_REFFERER}",
        "--force-media-title={}".format(
            "Rise and live again. As my fist of vengeance. As my Moon Knight."
        ),
    ]

    mpv_process = subprocess.Popen(args)

    mpv_process.wait()
