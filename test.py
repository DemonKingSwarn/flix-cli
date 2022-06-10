#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import httpx

import sys
import re
import subprocess
import time
import argparse

headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'

}

client = httpx.Client(headers=headers)

MPV_EXECUTABLE = "mpv"
DEFAULT_REFFERER = "https://dood.to"
md5_regex = r"/(pass_md5/.+?)'"
base_url = "https://allmoviesforyou.net"

def get_tv(query):

    series = query
    series = series.replace(" ", "-")
    
    get_tv.season = input("Enter season: ")
    get_tv.episode = input("Enter episode: ")

    url = f"{base_url}/episode/{series}-{get_tv.season}x{get_tv.episode}"

    get_data(url)

def get_data(url):

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

    get_data.link = f"{r.text}doodstream?token={token}&expiry={int(time.time() * 1000)}"


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--tv", help="Play TV series")

arg = parser.parse_args()

if arg.tv:
    query = "".join(sys.argv[2:])
    get_tv(query)
else:
    print("No argument specified.")
    exit(0)

def play(link):
    args = [
        MPV_EXECUTABLE,
        f"{link}",
        f"--referrer={DEFAULT_REFFERER}",
        "--force-media-title={}".format(
        f"{query} S{get_tv.season} E{get_tv.episode}"
        ),
    ]

    mpv_process = subprocess.Popen(args)

    mpv_process.wait()

play(get_data.link)
