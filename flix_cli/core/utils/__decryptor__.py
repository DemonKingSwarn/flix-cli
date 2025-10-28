import hashlib
import sys

import httpx
import regex

from ..__version__ import  __core_

headers = {
    "User-Agent": f"flix-cli/{__core__}",
    "Referer": "https://flixhq.to/",
    "X-Requested-With": "XMLHttpRequest"
}

client = httpx.Client(headers=headers, follow_redirects=True, timeout=None)

API_URL = "https://dec.eatmynerds.live"

def solve_challenge(challenge_response):
        """Solve the POW challenge"""
        payload = regex.search(r'"payload":"([^"]*)"', challenge_response).group(1)
        signature = regex.search(r'"signature":"([^"]*)"', challenge_response).group(1)
        difficulty = int(regex.search(r'"difficulty":([0-9]*)', challenge_response).group(1))
        
        challenge = payload.split('.')[0]
        prefix = '0' * difficulty
        
        nonce = 0
        while True:
            text_to_hash = f"{challenge}{nonce}"
            hash_val = hashlib.sha256(text_to_hash.encode()).hexdigest()
            
            if hash_val.startswith(prefix):
                break
            nonce += 1
        
        return payload, signature, nonce

def decrypt_stream_url(embed_link):
        """Extract video and subtitle links from embed"""
        # Get challenge
        challenge_response = client.get(f"{API_URL}/challenge")
        
        if not challenge_response.text:
            print("ERROR: Failed to get challenge response", file=sys.stderr)
            return None, None
        
        payload, signature, nonce = solve_challenge(challenge_response.text)
        
        # Get final data
        final_url = f"{API_URL}/?url={embed_link}&payload={payload}&signature={signature}&nonce={nonce}"
        json_response = client.get(final_url)
        json_data = json_response.json()
        
        # Extract video link
        video_link = None
        if 'sources' in json_data:
            for source in json_data['sources']:
                if 'file' in source and '.m3u8' in source['file']:
                    video_link = source['file']
                    break
        
        # Apply quality if specified
        if video_link and quality:
            video_link = regex.sub(r'/playlist\.m3u8', f'/{quality}/index.m3u8', video_link)
        
        # Extract subtitle links
        subs_links = []
        if 'tracks' in json_data:
            for track in json_data['tracks']:
                if 'file' in track and 'label' in track:
                    if regex.search(rf'{subs_language}', track['label'], regex.IGNORECASE):
                        subs_links.append(track['file'])
        
        return video_link, subs_links
