import subprocess

FFMPEG_EXECUTABLE = "ffmpeg"

def download(path, name, file, referer):

    name = name.replace(" ", "-")
    name = name.replace("\"", "")
    url = file

    subprocess.call(f"{FFMPEG_EXECUTABLE} -referer {referer} -i \"{url}\" -c copy \"{path}/{name}.mp4\"", shell=True)

    print(f"Downloaded at {path}/{name}.mp4")

