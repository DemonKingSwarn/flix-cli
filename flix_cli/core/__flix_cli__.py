import httpx
import base64
from Cryptodome.Cipher import AES
import regex as re
import subprocess
import platform
import os

from .utils.__player__ import play
from .utils.__downloader__ import download

try:
    import orjson as json
except ImportError:
    import json


from colorama import Fore, Style
import sys


def pad(data):
    return data + chr(len(data) % 16) * (16 - len(data) % 16)


def aes_encrypt(data: str, *, key, iv):
    return base64.b64encode(
        AES.new(key, AES.MODE_CBC, iv=iv).encrypt(pad(data).encode())
    )


def aes_decrypt(data: str, *, key, iv):
    return (
        AES.new(key, AES.MODE_CBC, iv=iv)
        .decrypt(base64.b64decode(data))
        .strip(b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10")
    )


client = httpx.Client()
cyan = lambda a: f"{Fore.CYAN}{a}{Style.RESET_ALL}"

SECRET = b"25742532592138496744665879883281"
IV = b"9225679083961858"

ENCRYPT_AJAX_ENDPOINT = "https://membed.net/encrypt-ajax.php"

DEFAULT_MEDIA_REFERER = "https://membed.net"

GDRIVE_PLAYER_M_ENDPOINT = "https://database.gdriveplayer.us/player.php"
GDRIVE_PLAYER_S_ENDPOINT = "https://database.gdriveplayer.us/player.php?type=series"

CONTENT_ID_REGEX = re.compile(r"streaming\.php\?id=([^&?/#]+)")

#r = client.get(GDRIVE_PLAYER_ENDPOINT)

#link = "https://" + re.findall(r'<a href="(.*?)"',r.text)[2]

#yarl query to get id from link
#id = yarl.URL(link).query.get('id')

def movie():

    content_id = CONTENT_ID_REGEX.search(
            client.get(
                GDRIVE_PLAYER_M_ENDPOINT,
                params={
                    "imdb": get_id.imdb_ids[get_id.c-1],
                },
            ).text
        ).group(1)


    content = json.loads(
            aes_decrypt(
                json.loads(
                    httpx.get(
                        ENCRYPT_AJAX_ENDPOINT,
                        params={"id": aes_encrypt(content_id, key=SECRET, iv=IV).decode()},
                        headers={"x-requested-with": "XMLHttpRequest"},
                    ).text
                )["data"],
                key=SECRET,
                iv=IV,
            )
        )

    #print(content)

    movie.subtitles = (_.get("file") for _ in content.get("track", {}).get("tracks", []))

    media = (content.get("source", []) or []) + (content.get("source_bk", []) or [])

    if not media:
        raise RuntimeError("Could not find any media for playback.")

    if len(media) > 2:
        for content_index, source in enumerate(media):
            if(content_index+1 != len(media)):
                print(f" > {content_index+1} / {source['label']} / {source['type']}")
        try:
            while not (
                (user_selection := input("Take it or leave it, index: ")).isdigit()
                and (parsed_us := int(user_selection)-1) in range(content_index)
            ):
                print("Nice joke. Now you have to TRY AGAIN!!!")
            movie.selected = media[parsed_us]
        except KeyboardInterrupt:
            exit(0)
    else:   
        movie.selected = media[0]

def series():
    season = input("Enter season: ")
    episode = input("Enter episode: ")
    
    
    content_id = CONTENT_ID_REGEX.search(
            client.get(
                GDRIVE_PLAYER_S_ENDPOINT,
                params={
                    "imdb": get_id.imdb_ids[get_id.c-1],
                    "season": season,
                    "episode": episode,
                },
            ).text
        ).group(1)

    content = json.loads(
            aes_decrypt(
                json.loads(
                    httpx.get(
                        ENCRYPT_AJAX_ENDPOINT,
                        params={"id": aes_encrypt(content_id, key=SECRET, iv=IV).decode()},
                        headers={"x-requested-with": "XMLHttpRequest"},
                    ).text
                )["data"],
                key=SECRET,
                iv=IV,
            )
        )


    series.subtitles = (_.get("file") for _ in content.get("track", {}).get("tracks", []))

    media = (content.get("source", []) or []) + (content.get("source_bk", []) or [])

    if not media:
        raise RuntimeError("Could not find any media for playback.")

    if len(media) > 2:
        for content_index, source in enumerate(media):
            if(content_index+1 != len(media)):
                print(f" > {content_index+1} / {source['label']} / {source['type']}")
        try:
            while not (
                (user_selection := input("Take it or leave it, index: ")).isdigit()
                and (parsed_us := int(user_selection)-1) in range(content_index)
            ):
                print("Nice joke. Now you have to TRY AGAIN!!!")
            series.selected = media[parsed_us]
        except KeyboardInterrupt:
            exit(0)
    else:   
        series.selected = media[0]


def get_id(query: str):
    query = query.replace(" ","_")
    
    url = f"https://v2.sg.media-imdb.com/suggestion/{query[0]}/{query}.json"
    
    r=client.get(url)
    
    get_id.imdb_ids = [i["id"] for i in r.json().get("d")]
    names = [i["l"] for i in r.json().get("d")]
    
    print(cyan("[*]Results: "))
    print("\n")
    for i in range(len(names)):
        print(cyan(f"{i+1}. {names[i]}"))
    
    print("\n")    
    get_id.c = int(input(cyan("[*]Enter number: ")))
    
    return get_id.imdb_ids[get_id.c-1]


if len(sys.argv) == 1:
    query = input("Search: ")
    if query == "":
        print("ValueError: no query parameter provided")
        exit(0)
else:
    query = " ".join(sys.argv[1:])

get_id(query)

def poison():
    print("\nChoose your poison!!!")
    print("[m] movie\n[s] series\n[q] quit")

    ch = input(": ")

    if ch == "m":
        movie()
    elif ch == "s":
        series()
    else:
        exit(0)

poison()

#print(selected)

def determine_path() -> str:
    
    plt = platform.system()

    if plt == "Windows":
        return f"C://Users//{os.getenv('username')}//Downloads"
    
    elif (plt == "Linux"):
        return f"/home/{os.getlogin()}/Downloads"
    
    elif (plt == "Darwin"):
        return f"/Users/{os.getlogin()}/Downloads"

    else:
        print("[!] Make an issue for your OS.")
        exit(0)

def dlData(path: str = determine_path()):
    try:
        dl(movie.selected, path)
    except Exception as e:
        dl(series.selected, path)

def dl(selected, path):
    download(path, query, selected['file'], DEFAULT_MEDIA_REFERER)

def provideData():
    try:
        launchPlayer(movie.selected, movie.subtitles)
    except Exception as e:
        launchPlayer(series.selected, series.subtitles)

def launchPlayer(selected, subtitles):
    play(selected['file'], query, DEFAULT_MEDIA_REFERER, subtitles)


def init():
    print("\n[p] play\n[d] download\n[q] quit")

    ch = input(": ")

    if ch == "p":
        provideData()
    elif ch == "d":
        dl()
    else:
        exit(0)

#main()

init()
