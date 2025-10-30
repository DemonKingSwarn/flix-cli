import subprocess
import os

import httpx

#FFMPEG_EXECUTABLE = "ffmpeg"
YT_DLP_EXECUTABLE = "yt-dlp"

FLIX_CLI_DOWNLOADS="flix-cli"

client = httpx.Client(timeout=None)

def download(path, name, file, referer, subs):

    name = name.replace(" ", "-")
    name = name.replace("\"", "")
    url = file
    if not os.path.exists(f"{path}/{FLIX_CLI_DOWNLOADS}"):
        os.makedirs(f"{path}/{FLIX_CLI_DOWNLOADS}")
    
    path = f"{path}/{FLIX_CLI_DOWNLOADS}"
    #subprocess.call(f"{FFMPEG_EXECUTABLE} -referer {referer} -i \"{url}\" -c copy \"{path}/{name}.mp4\"", shell=True)
    subprocess.call(f"{YT_DLP_EXECUTABLE} \"{url}\" --downloader ffmpeg -o \"{path}/{name}.mp4\"", shell=True)

    sub = subs[0]
    resp = client.get(sub)

    with open(f"{path}/{name}.vtt", 'wb') as f:
        f.write(resp.content)

    print(f"Downloaded at {path}/{name}.mp4 and {path}/{name}.vtt")

