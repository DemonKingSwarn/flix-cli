import platform as plt
import subprocess
import urllib.parse

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
            safe_file = urllib.parse.quote(file)
            safe_subs = urllib.parse.quote(','.join(subtitles))

            vlc_url = f"vlc-x-callback://x-callback-url/stream?url={safe_file}&sub={safe_subs}"

            subprocess.run([
                "am",
                "start",
                "-a",
                "android.intent.action.VIEW",
                "-d",
                f"{vlc_url}"
            ], check=True, capture_output=True)

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
