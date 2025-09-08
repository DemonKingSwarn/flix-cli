import platform as plt
import subprocess

MPV_EXECUTABLE = "mpv"
IINA_EXECUTABLE = "iina"


def play(file, name, referer, subtitles):
    try:
        if(plt.system() == 'Linux' or plt.system() == 'Windows'):
            args = [
                MPV_EXECUTABLE,
                file,
                f"--referrer={referer}",
                f"--force-media-title=Playing {name}",
            ]
            args.extend(f"--sub-file={_}" for _ in subtitles)

            mpv_process = subprocess.Popen(args, stdout=subprocess.DEVNULL)

            mpv_process.wait()

        elif(plt.system() == 'Darwin'):
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

