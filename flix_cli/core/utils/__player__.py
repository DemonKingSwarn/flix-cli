import platform as plt
import subprocess
from pathlib import Path

import httpx

from .__config__ import get_config

MPV_EXECUTABLE = "mpv"
IINA_EXECUTABLE = "iina"

client = httpx.Client(timeout=None)

def check_android() -> bool:
    try:
        cmd = subprocess.check_output(["uname", "-o"])
        res = cmd.decode("utf-8").strip()

        return res == "Android"

    except (FileNotFoundError, subprocess.SubprocessError):
        return False


def download_sub_as_srt(url: str, out_dir: str) -> Path:
     out_dir.mkdir(parents=True, exist_ok=True)

     srt_path = out_dir / "sub.srt"

     r = client.get(url)

     srt_path.write_bytes(r.content)

     return srt_path

def play(file: str, name: str, referer: str, subtitles: list[str]) -> None:
    player, _ = get_config()
    system = plt.system()

    try:
        if not isinstance(player, str):
            player = "mpv"
    except NameError:
        player = "mpv"

    try:
        if check_android():
            print("~ Android Detected ~")

            args = [
                "am",
                "start",
                "--user",
                "0",
                "-a",
                "android.intent.action.VIEW",
                "-d",
                f"{file}",
                "-n", "org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity",
                "-e", "title", f"Playing {name}"
            ]

            sub_path = download_sub_as_srt(subtitles[0], Path("/data/data/com.termux/files/flix-cli"))
            sub_uri = "content://com.termux.fileprovider/root" + str(sub_path)
            args.extend(["--es", "subtitles_location", f"{sub_uri}"])
            subprocess.run(args, check=True, capture_output=True)

            print(f"~ Opened in VLC ~")

        elif system in {"Linux", "Windows", "FreeBSD"}:
            args = [
                MPV_EXECUTABLE,
                file,
                f"--referrer={referer}",
                f"--force-media-title=Playing {name}",
            ]
            args.extend(f"--sub-file={_}" for _ in subtitles)

            mpv_process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            mpv_process.wait()

        elif system == "Darwin":
            args = [
                IINA_EXECUTABLE,
                "--no-stdin",
                "--keep-running",
                f"--mpv-referrer={referer}",
                file,
                f"--mpv-force-media-title=Playing {name}",
            ]
            args.extend(f"--mpv-sub-files={_}" for _ in subtitles)

            iina_process = subprocess.Popen(args, stdout=subprocess.DEVNULL)
            iina_process.wait()

    except Exception:
        print("[!] no supported video player were found.")
        exit(1)
