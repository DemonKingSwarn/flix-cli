import subprocess

MPV_EXECUTABLE = "mpv"
IINA_EXECUTABLE = "iina"

def play(file, name, referer, subtitles):
    try:
        try:
            args = [
                MPV_EXECUTABLE,
                file,
                f"--referrer={referer}",
                f"--force-media-title=Playing {name}",
            ]
            args.extend(f"--sub-file={_}" for _ in subtitles)

            mpv_process = subprocess.Popen(args)

            mpv_process.wait()

        except Exception as e:
            args = [
                IINA_EXECUTABLE,
                f"--mpv-referrer={referer}",
                file,
                f"--mpv-force-media-title=Playing {name}",
                "--keep-running"
            ]

            args.extend(f"--mpv-sub-files={_}" for _ in subtitles)
            
            iina_process = subprocess.Popen(args)

            iina_process.wait()

    except Exception as e:
        print("[!] mpv or iina not found.")
        exit(1)

