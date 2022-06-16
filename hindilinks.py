#!/usr/bin/env python3

import httpx
from bs4 import BeautifulSoup as bs

import re
import os

"""
links
1.streamtape
2.doodstream
3.mixdrop
4.vupload
5.videobin
"""

client = httpx.Client(headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'})

#show_url = "https://hindilinks4u.vip/ardh-2022/"
show_url = f"https://hindilinks4u.vip/777-charlie-2022/"

r=client.get(show_url)
soup=bs(r.text,"html.parser")

#collect all the links
links = [i["href"] for i in soup.select(".video-tabs a")]
print(links)

#using the streamtape link for this one
stream_link = links[0]

r=client.get(stream_link)

try:
    url_slug= re.findall(r"'norobotlink'\)\.innerHTML = '(.+?)' \+ \('xcd(.+?)'\)",r.text)[0]
except:
    print("[*]Not available on streamtape")
    exit()

final_url = "https:{}".format("".join(url_slug))

final_link = client.get(final_url).headers.get("location")

os.system(f'mpv "{final_link}"')
