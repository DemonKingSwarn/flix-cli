import hashlib

import httpx
import re

client = httpx.Client(follow_redirects=True, timeout=None)

def decrypt_stream_url(embed_link, api_url):
    # Step 1: Obtain challenge
    challenge_resp = client.get(f"{api_url}/challenge")
    if challenge_resp.status_code != 200:
        print(f"Failed to get challenge: {challenge_resp.status_code}")
        return None, []

    response_text = challenge_resp.text
    try:
        payload_match = re.search(r'"payload":"([^"]*)"', response_text)
        payload = payload_match.group(1) if payload_match else None
        signature_match = re.search(r'"signature":"([^"]*)"', response_text)
        signature = signature_match.group(1) if signature_match else None
        difficulty_match = re.search(r'"difficulty":([0-9]*)', response_text)
        difficulty = int(difficulty_match.group(1)) if difficulty_match else 0
        challenge = payload.split(".")[0] if payload else ""
    except (AttributeError, IndexError):
        payload, signature, difficulty, challenge = None, None, 0, None

    if not (payload and signature and challenge and difficulty):
        print("Challenge response missing required fields.")
        return None, []
    # Step 2: Brute-force nonce to meet difficulty
    prefix = '0' * difficulty
    nonce = 0
    while True:
        text_to_hash = f"{challenge}{nonce}"
        hashval = hashlib.sha256(text_to_hash.encode('utf-8')).hexdigest()
        if hashval.startswith(prefix):
            break
        nonce += 1
    # Step 3: Request the decrypted video metadata
    params = {
        "url": embed_link,
        "payload": payload,
        "signature": signature,
        "nonce": nonce
    }
    resp = client.get(api_url, params=params)
    if resp.status_code != 200:
        print(f"Decoder request failed: {resp.status_code}")
        return None, []
    data = resp.json()
    # Extract the streaming URL and subtitles from response (as before)
    video_link = None
    subtitles = []
    if 'file' in data and '.m3u8' in data['file']:
        video_link = data['file']
    if 'tracks' in data:
        for track in data['tracks']:
            if track.get('kind') == 'captions' and track.get('file'):
                subtitles.append(track['file'])
    return video_link, subtitles
