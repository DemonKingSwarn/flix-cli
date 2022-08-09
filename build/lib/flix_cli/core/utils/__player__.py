import platform
import subprocess

MPV_EXECUTABLE = "mpv"
IINA_EXECUTABLE = "iina"

VLC_INTENT = "am start -a \"android.intent.action.VIEW\""

def play(file, name, referer, subtitles):
    try:
        if(subprocess.check_output(['uname', '-o']).strip() == b'Android'):
            subprocess.call(f"curl -sL {subtitles} -o /storage/emulated/0/subs.srt", shell=True)
            subprocess.call(f"{VLC_INTENT} -d {file} -n org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity -e \"title\" \"Playing {name}\" -e \"subtitles_location\" \"/storage/emulated/0/subs.srt\"", shell=True)

        elif(platform.system() == "Linux"):
            args = [
                MPV_EXECUTABLE,
                file,
                f"--referrer={referer}",
                f"--force-media-title=Playing {name}",
            ]
            args.extend(f"--sub-file={_}" for _ in subtitles)
            print(f"{_}" for _ in subtitles)

            mpv_process = subprocess.Popen(args, stdout=subprocess.DEVNULL)

            mpv_process.wait()

        elif(platform.system() == "Darwin"):
            args = [
                IINA_EXECUTABLE,
                f"--mpv-referrer={referer}",
                file,
                f"--mpv-force-media-title=Playing {name}",
                "--keep-running"
            ]

            args.extend(f"--mpv-sub-files={_}" for _ in subtitles)
            
            iina_process = subprocess.Popen(args, stdout=subprocess.DEVNULL)

            iina_process.wait()

    except Exception as e:
        print("[!] no supported video player were found.")
        exit(1)

