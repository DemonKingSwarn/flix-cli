import hashlib
import sys

import httpx
import regex as re

from .__version__ import  __core_

headers = {
    "User-Agent": f"flix-cli/{__core__}",
    "Referer": "https://flixhq.to/",
    "X-Requested-With": "XMLHttpRequest"
}

client = httpx.Client(headers=headers, follow_redirects=True, timeout=None)

def send_notification(message):
    print(message, file=sys.stderr)

def decrypt_stream_url(embed_link, API_URL):
    client = httpx.Client()

    try:
        response = client.get(f"{API_URL}/challenge")
        response.raise_for_status()
        challenge_response = response.text
    except Exception as e:
        send_notification(f"ERROR: Failed to get a response from the API server. ({e})")
        return None, None

    payload_match = re.search(r'"payload":"([^"]+)"', challenge_response)
    signature_match = re.search(r'"signature":"([^"]+)"', challenge_response)
    difficulty_match = re.search(r'"difficulty":(\d+)', challenge_response)

    if not (payload_match and signature_match and difficulty_match):
        send_notification("FATAL: Could not parse the API challenge response.")
        return None, None

    payload = payload_match.group(1)
    signature = signature_match.group(1)
    difficulty = int(difficulty_match.group(1))
    challenge = payload.split('.')[0]

    prefix = '0' * difficulty
    nonce = 0

    while True:
        text_to_hash = f"{challenge}{nonce}"
        hash_val = hashlib.sha256(text_to_hash.encode()).hexdigest()

        if hash_val.startswith(prefix):
            break
        nonce += 1

    final_url = f"{API_URL}/?url={embed_link}&payload={payload}&signature={signature}&nonce={nonce}"

    try:
        json_data = client.get(final_url).text
    except Exception as e:
        send_notification(f"ERROR: Failed to get JSON data. ({e})")
        return None, None

    # Step 5: Extract main video and subtitle links
    video_match = re.search(r'"file":"([^"]*\.m3u8)"', json_data)
    subs_matches = re.findall(r'"file":"([^"]*\.vtt)"', json_data, flags=re.IGNORECASE)

    video_link = video_match.group(1) if video_match else None
    subs_links = subs_matches if subs_matches else []

    return video_link, subs_links

