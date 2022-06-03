#!/usr/bin/env python3

import base64
import re
import subprocess

import httpx
from Cryptodome.Cipher import AES

try:
    import orjson as json
except ImportError:
    import json


MPV_EXECUTABLE = "mpv"

DEFAULT_MEDIA_REFERER = "https://membed.net"


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


CONTENT_ID_REGEX = re.compile(r"streaming\.php\?id=([^&?/#]+)")

SECRET = b"25742532592138496744665879883281"
IV = b"9225679083961858"


ENCRYPT_AJAX_ENDPOINT = "https://membed.net/encrypt-ajax.php"
GDRIVE_PLAYER_ENDPOINT = "https://database.gdriveplayer.us/player.php"

client = httpx.Client()


imdb_id = input("Hand me the IMDB or, just press nothingness: ") or "tt1877830"


content_id = CONTENT_ID_REGEX.search(
    client.get(
        GDRIVE_PLAYER_ENDPOINT,
        params={
            "imdb": imdb_id,
        },
    ).text
).group(1)


content = json.loads(
    aes_decrypt(
        json.loads(
            client.get(
                ENCRYPT_AJAX_ENDPOINT,
                params={"id": aes_encrypt(content_id, key=SECRET, iv=IV).decode()},
                headers={"x-requested-with": "XMLHttpRequest"},
            ).text
        )["data"],
        key=SECRET,
        iv=IV,
    )
)

subtitles = (_.get("file") for _ in content.get("track", {}).get("tracks", []))

media = (content.get("source", []) or []) + (content.get("source_bk", []) or [])

for content_index, source in enumerate(media):
    print(f" > {content_index} / {source['label']} / {source['type']}")

if not media:
    raise RuntimeError("Could not find any media for playback.")

if len(media) > 1:
    while not (
            (user_selection := input("Take it or leave it, index: ")).isdigit()
        and (parsed_us := int(user_selection)) in range(content_index)
    ):
        print("Nice joke. Now you have to TRY AGAIN!!!")
    selected = media[parsed_us]
else:
    selected = media[0]

args = [
    MPV_EXECUTABLE,
    selected["file"],
    f"--referrer={DEFAULT_MEDIA_REFERER}",
    "--force-media-title={}".format(
        "Rise and live again. As my fist of vengeance. As my Moon Knight."
    ),
]
args.extend(f"--sub-file={_}" for _ in subtitles)


mpv_process = subprocess.Popen(args)

mpv_process.wait()
