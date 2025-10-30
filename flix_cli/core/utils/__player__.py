import platform as plt
import subprocess
import os

MPV_EXECUTABLE = "mpv"
IINA_EXECUTABLE = "iina"

def is_ish():
    try:
        output = subprocess.check_output(['uname', '-o'], text=True).strip()
        return output == 'iSH'
    except Exception:
        return False

def is_android():
    try:
        uname = subprocess.check_output(['uname', '-o'], text=True).strip()
        return uname == 'Android'
    except Exception:
        return False

def play(file, name, referer, subtitles):
    try:
        if is_android():
            subprocess.call(f"{MPV_EXECUTABLE} {file} {','.join(subtitles)}")

        elif(plt.system() == "Linux" or plt.system() == "Windows" or plt.system() == "FreeBSD"):
            args = [
                MPV_EXECUTABLE,
                file,
                f"--referrer={referer}",
                f"--force-media-title=Playing {name}",
            ]
            args.extend(f"--sub-file={_}" for _ in subtitles)

            mpv_process = subprocess.Popen(args, stdout=subprocess.DEVNULL)

            mpv_process.wait()

        elif(plt.system() == "Darwin"):
            if is_ish():
                print(f"\033]8;;vlc-x-callback://x-callback-url/stream?url={file}&sub={','.join(subtitles)}\a~ Tap to open VLC ~\033]8;;\a")

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

    except Exception as e:
        print("[!] no supported video player were found.")
        exit(1)

