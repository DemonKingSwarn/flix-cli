import subprocess
from pathlib import Path

import httpx

from .__config__ import get_config

YT_DLP_EXECUTABLE = "yt-dlp"

FLIX_CLI_DOWNLOADS = "flix-cli"

client = httpx.Client(timeout=None)


def download(path: Path, name: str, file: str, referer: str, subs: list[str]) -> None:
    _, dl_path = get_config()
    dl_path = Path(dl_path)

    name = name.replace(" ", "-")
    name = name.replace('"', "")
    url = file

    if dl_path.exists():
        path = dl_path

    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    path /= FLIX_CLI_DOWNLOADS

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
