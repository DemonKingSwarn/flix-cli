import subprocess

MPV_EXECUTABLE = "mpv"
VLC_EXECUTABLE = "vlc"

def play(file, name, referer, subtitles):
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
            VLC_EXECUTABLE,
            f"--http-referrer={referer}",
            file,
            f"--meta-title=Playing {name}"
        ]
            
        vlc_process = subprocess.Popen(args)

        vlc_process.wait()

