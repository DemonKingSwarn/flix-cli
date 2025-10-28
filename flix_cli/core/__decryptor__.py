import hashlib
import time

import httpx

from .__version__ import __core__

headers = {
    "User-Agent": f"flix-cli/{__core__}",
    "Referer": "https://flixhq.to/",
    "X-Requested-With": "XMLHttpRequest"
}

client = httpx.Client(headers=headers, follow_redirects=True, timeout=None)

def decrypt_stream_url(embed_link, api_url):
    # Step 1: Get challenge info from API
    resp = client.get(f"{api_url}/challenge")
    if resp.status_code != 200:
        print(f"Failed to fetch challenge ({resp.status_code})")
        return embed_link, []

    data = resp.json()
    payload = data.get("payload")
    signature = data.get("signature")
    difficulty = int(data.get("difficulty", 0))
    if not (payload and signature and difficulty):
        print("Missing challenge data fields")
        return embed_link, []

    challenge = payload.split(".")[0]  # Part before dot as in shell

    # Step 2: Solve proof-of-work: find nonce so sha256(challenge+nonce) starts with difficulty zeros
    prefix = "0" * difficulty
    nonce = 0
    while True:
        text = f"{challenge}{nonce}"
        hash_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if hash_digest.startswith(prefix):
            break
        nonce += 1

    # Step 3: Final request with solved nonce and challenge data
    params = {
        "url": embed_link,
        "payload": payload,
        "signature": signature,
        "nonce": nonce
    }
    final_resp = client.get(api_url, params=params)
    if final_resp.status_code != 200:
        print(f"Failed to get decrypted url from decoder ({final_resp.status_code})")
        return embed_link, []

    final_data = final_resp.json()

    # Extract video link and subtitles as before
    video_link = final_data.get("file") or ""
    subtitles = []
    if "tracks" in final_data:
        for track in final_data["tracks"]:
            if track.get("kind") == "captions" and track.get("file"):
                subtitles.append(track["file"])

    return video_link, subtitles
