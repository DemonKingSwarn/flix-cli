import hashlib
import sys

import httpx
import regex as re

client = httpx.Client(follow_redirects=True, timeout=None)

def send_notification(message):
    print(message, file=sys.stderr)

def decrypt_stream_url(embed_link, API_URL):
    quality = None
    json_output = False
    no_subs = False
    subs_language = "en"

    # Step 1: Get challenge from API
    try:
        response = client.get(f"{API_URL}/challenge")
        response.raise_for_status()
        challenge_response = response.text
    except Exception as e:
        send_notification(f"ERROR: Failed to get a response from the API server. ({e})")
        return None

    # Step 2: Extract fields using regex
    payload_match = re.search(r'"payload":"([^"]+)"', challenge_response)
    signature_match = re.search(r'"signature":"([^"]+)"', challenge_response)
    difficulty_match = re.search(r'"difficulty":(\d+)', challenge_response)

    if not (payload_match and signature_match and difficulty_match):
        send_notification("FATAL: Could not parse the API challenge response.")
        return None

    payload = payload_match.group(1)
    signature = signature_match.group(1)
    difficulty = int(difficulty_match.group(1))
    challenge = payload.split('.')[0]

    # Step 3: Proof-of-work
    prefix = '0' * difficulty
    nonce = 0

    while True:
        text_to_hash = f"{challenge}{nonce}"
        hash_val = hashlib.sha256(text_to_hash.encode()).hexdigest()

        if hash_val.startswith(prefix):
            break
        nonce += 1

    # Step 4: Build final URL and request data
    final_url = f"{API_URL}/?url={embed_link}&payload={payload}&signature={signature}&nonce={nonce}"
    json_data = client.get(final_url).text

    # Step 5: Extract .m3u8 link
    m3u8_match = re.search(r'"file":"([^"]*\.m3u8)"', json_data)
    video_link = m3u8_match.group(1) if m3u8_match else None

    if quality and video_link:
        video_link = video_link.replace("/playlist.m3u8", f"/{quality}/index.m3u8")

    if json_output:
        print(json_data)
        sys.exit(0)

    # Step 6: Handle subtitles
    subs_links = []

    if no_subs:
        send_notification("Continuing without subtitles")
    else:
        subs_links = re.findall(
            rf'"file":"([^"]*)"[^{{}}]*"label":"[^"]*{subs_language}[^"]*"', json_data, flags=re.IGNORECASE
        )
        if not subs_links:
            send_notification(f"No subtitles found for language '{subs_language}'")

    return video_link, subs_links

