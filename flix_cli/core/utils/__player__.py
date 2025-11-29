import platform as plt
import subprocess

import httpx

from .__config__ import get_config

MPV_EXECUTABLE = "mpv"
IINA_EXECUTABLE = "iina"

client = httpx.Client(timeout=None)


def is_ish() -> bool:
    try:
        output = subprocess.check_output(["uname", "-o"], text=True).strip()
        return output == "iSH"
    except Exception:
        return False


def check_android() -> str:
    cmd = subprocess.check_output(["uname", "-o"])
    res = cmd.decode("utf-8").strip()

    return res == "Android"


def play(file: str, name: str, referer: str, subtitles: list[str]) -> None:
    player, _ = get_config()
    system = plt.system()

    try:
        if not isinstance(player, str):
            player = "mpv"
    except NameError:
        player = "mpv"

    try:
        if system in {"Linux", "Windows", "FreeBSD"}:
            if check_android():
                vlc_url = f"vlc-x-callback://x-callback-url/stream?url={file}&sub={','.join(subtitles)}"

                subprocess.run([
                    "am",
                    "start",
                    "-a",
                    "android.intent.action.VIEW",
                    "-d",
                    f"{vlc_url}"
                ], check=True, capture_output=True) 
            
            else:
                if player == "mpv":
                    args = [
                        MPV_EXECUTABLE,
                        file,
                        f"--referrer={referer}",
                        f"--force-media-title=Playing {name}",
                    ]
                    args.extend(f"--sub-file={_}" for _ in subtitles)

                    mpv_process = subprocess.Popen(
                        args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    mpv_process.wait()

        elif system == "Darwin":
            if is_ish():
                print(
                    f"\033]8;;vlc-x-callback://x-callback-url/stream?url={file}&sub={','.join(subtitles)}\a~ Tap to open VLC ~\033]8;;\a"
                )

            else:
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
