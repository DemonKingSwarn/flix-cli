import hashlib
import json
import sys

import httpx
import regex

headers = {"User-Agent": "curl/8.16.0"}

client = httpx.Client(headers=headers, follow_redirects=True, timeout=None)

API_URL = "https://dec.eatmynerds.live"

def decrypt_stream_url(embed_link, quality=None, subs_language="english"):
    params = {
        "url": embed_link
    }
    
    response = client.get(API_URL, params=params)

    if response.status_code != 200:
        print(f"ERROR: {response.text}", file=sys.stderr)
        return None, None

    try:
        json_data = response.json()
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}", file=sys.stderr)
        print(f"Response was: {response.text}", file=sys.stderr)
        return None, None

    video_link = None
    if "sources" in json_data:
        for source in json_data["sources"]:
            if "file" in source and ".m3u8" in source["file"]:
                video_link = source["file"]
                break

    if video_link and quality:
        video_link = regex.sub(r"/playlist\.m3u8", f"/{quality}/index.m3u8", video_link)

    subs_links = []
    if "tracks" in json_data:
        for track in json_data["tracks"]:
            if "file" in track and "label" in track:
                if regex.search(rf"{subs_language}", track["label"], regex.IGNORECASE):
                    subs_links.append(track["file"])

    return video_link, subs_links
