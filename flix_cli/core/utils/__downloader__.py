import os
import subprocess

import httpx

from .__config__ import get_config

YT_DLP_EXECUTABLE = "yt-dlp"

FLIX_CLI_DOWNLOADS = "flix-cli"

client = httpx.Client(timeout=None)


def download(path: str, name: str, file: str, referer: str, subs: list[str]) -> None:
    _, dl_path = get_config()

    name = name.replace(" ", "-")
    name = name.replace('"', "")
    url = file

    if os.path.exists(dl_path):
        path = dl_path

    if not os.path.exists(f"{path}/{FLIX_CLI_DOWNLOADS}"):
        os.makedirs(f"{path}/{FLIX_CLI_DOWNLOADS}")

    path = f"{path}/{FLIX_CLI_DOWNLOADS}"

    args = [
        YT_DLP_EXECUTABLE,
        f"{url}",
        "--no-skip-unavailable-fragments",
        "--fragment-retries",
        "infinite",
        "-N",
        "16",
        "-o",
        f"{path}/{name}.mp4",
    ]

    yt_dl_process = subprocess.Popen(args)
    yt_dl_process.wait()

    sub = subs[0]
    resp = client.get(sub)

    with open(f"{path}/{name}.vtt", "wb") as f:
        f.write(resp.content)

    print(f"Downloaded at {path}/{name}.mp4 and {path}/{name}.vtt")
