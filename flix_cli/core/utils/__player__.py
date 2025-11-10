import platform as plt
import subprocess

import httpx

from .__config__ import get_config

MPV_EXECUTABLE = "mpv"
IINA_EXECUTABLE = "iina"
# VLC_EXECUTABLE = "vlc"

client = httpx.Client(timeout=None)


def is_ish() -> bool:
    try:
        output = subprocess.check_output(["uname", "-o"], text=True).strip()
        return output == "iSH"
    except Exception:
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
        if system in {"Linux", "Windows", "FreeBSD"}:
            if player == "mpv":
                args = [
                    MPV_EXECUTABLE,
                    file,
                    f"--referrer={referer}",
                    f"--force-media-title=Playing {name}",
                ]
                args.extend(f"--sub-file={_}" for _ in subtitles)

                mpv_process = subprocess.Popen(args, stdout=subprocess.DEVNULL)
                mpv_process.wait()

            """
            elif player == "vlc":
                args = [
                    VLC_EXECUTABLE,
                    f"{file}",
                    f"--http-referrer={referer}",
                    f"--input-title-format=Playing {name}",
                ]

                subs_path = get_temp()
                sub = subtitles[0]
                resp = client.get(sub)
                with open(f"{sub_path}/sub.vtt", 'wb') as f:
                    f.write(resp.content)

                args.extend(f"--sub-file={sub_path}/sub.vtt")

                vlc_process = subprocess.Popen(args, stdout=subprocess.DEVNULL)
                vlc_process.wait()
            """

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
