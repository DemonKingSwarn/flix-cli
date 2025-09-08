#!/usr/bin/env python3

import httpx
import regex as re
from fzf import fzf_prompt
import subprocess
import platform
import os

from .utils.__player__ import play
from .utils.__downloader__ import download
from .__version__ import __core__

try:
    import orjson as json
except ImportError:
    import json

import sys
from urllib.parse import urljoin, quote
import time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": f"flix-cli/{__core__}",
    "Referer": "https://flixhq.to/",
    "X-Requested-With": "XMLHttpRequest"
}

client = httpx.Client(headers=headers, follow_redirects=True, timeout=None)

FLIXHQ_BASE_URL = "https://flixhq.to"
FLIXHQ_SEARCH_URL = f"{FLIXHQ_BASE_URL}/search"
FLIXHQ_AJAX_URL = f"{FLIXHQ_BASE_URL}/ajax"
DECODER = "https://dec.eatmynerds.live"

selected_media = None
selected_subtitles = []

def decode_url(url: str):
    """Decode the stream URL using the decoding service"""
    try:
        print(f"Debug: Decoding URL: {url}")
        decoder_endpoint = f"{DECODER}?url={quote(url)}"
        
        resp = client.get(decoder_endpoint, headers={
            "User-Agent": headers["User-Agent"],
            "Referer": FLIXHQ_BASE_URL
        })
        
        if resp.status_code == 200:
            try:
                data = resp.json()
                if 'sources' in data and data['sources']:
                    video_link = data['sources'][0].get('file', '')
                    if video_link and '.m3u8' in video_link:
                        print(f"Debug: Found m3u8 URL: {video_link}")
                        subtitles = []
                        if 'tracks' in data:
                            for track in data['tracks']:
                                if track.get('kind') == 'captions' and track.get('file'):
                                    subtitles.append(track['file'])
                        return video_link, subtitles
                
                # Try other common fields
                for key in ['link', 'url', 'file']:
                    if key in data and data[key]:
                        return data[key], []
                        
            except json.JSONDecodeError:
                text_response = resp.text
                m3u8_match = re.search(r'"file":"([^"]*\.m3u8[^"]*)"', text_response)
                if m3u8_match:
                    decoded_url = m3u8_match.group(1)
                    print(f"Debug: Regex extracted m3u8: {decoded_url}")
                    return decoded_url, []
        
        print(f"Debug: Failed to decode, using original URL")
        return url, []
        
    except Exception as e:
        print(f"Debug: Error decoding URL: {e}")
        return url, []

def search_content(query: str):
    """Search for content on flixhq.to"""
    try:
        search_params = query.replace(" ", "-")
        response = client.get(f"{FLIXHQ_SEARCH_URL}/{search_params}")
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='flw-item')
        
        if not items:
            print("No results found")
            return None
        
        results = []
        urls = []
        
        for i, item in enumerate(items[:10]):
            poster_link = item.find('div', class_='film-poster')
            detail_section = item.find('div', class_='film-detail')
            
            if poster_link and detail_section:
                link_elem = poster_link.find('a')
                title_elem = detail_section.find('h2', class_='film-name')
                
                if link_elem and title_elem:
                    href = link_elem.get('href', '')
                    title_link = title_elem.find('a')
                    title = title_link.get('title', 'Unknown Title') if title_link else 'Unknown Title'
                    
                    info_elem = detail_section.find('div', class_='fd-infor')
                    year = ""
                    content_type = ""
                    
                    if info_elem:
                        spans = info_elem.find_all('span')
                        if spans:
                            year = spans[0].text.strip() if spans else ""
                            if len(spans) > 1:
                                content_type = spans[1].text.strip()
                    
                    display_title = f"{i+1}. {title}"
                    if year:
                        display_title += f" ({year})"
                    if content_type:
                        display_title += f" [{content_type}]"
                    
                    results.append(display_title)
                    urls.append(urljoin(FLIXHQ_BASE_URL, href))
        
        if not results:
            print("No valid results found")
            return None
        
        selected = fzf_prompt(results)
        if not selected:
            return None
        
        selected_index = int(selected[0]) - 1
        return urls[selected_index]
        
    except Exception as e:
        print(f"Search failed: {e}")
        return None

def get_tv_seasons(media_id: str):
    """Get TV show seasons using lobster's approach"""
    try:
        seasons_url = f"{FLIXHQ_AJAX_URL}/v2/tv/seasons/{media_id}"
        
        response = client.get(seasons_url)
        print(f"Debug: Seasons URL: {seasons_url}")
        print(f"Debug: Seasons response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse like lobster: extract season title and ID from href
            season_pattern = re.compile(r'href="[^"]*-(\d+)"[^>]*>([^<]*)</a>')
            matches = season_pattern.findall(response.text)
            
            seasons = []
            for season_id, season_title in matches:
                seasons.append({
                    'id': season_id,
                    'title': season_title.strip()
                })
                print(f"Debug: Found season: {season_title.strip()} (ID: {season_id})")
            
            return seasons
        
        return []
        
    except Exception as e:
        print(f"Failed to get TV seasons: {e}")
        return []

def get_season_episodes(season_id: str):
    """Get episodes for a season using lobster's approach"""
    try:
        episodes_url = f"{FLIXHQ_AJAX_URL}/v2/season/episodes/{season_id}"
        
        response = client.get(episodes_url)
        print(f"Debug: Episodes URL: {episodes_url}")
        print(f"Debug: Episodes response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse like lobster: look for data-id and title in nav-item elements
            # First, split by class="nav-item" like lobster does
            content = response.text.replace('\n', '').replace('class="nav-item"', '\nclass="nav-item"')
            
            episode_pattern = re.compile(r'data-id="(\d+)"[^>]*title="([^"]*)"')
            matches = episode_pattern.findall(content)
            
            episodes = []
            for data_id, episode_title in matches:
                episodes.append({
                    'data_id': data_id,
                    'title': episode_title.strip()
                })
                print(f"Debug: Found episode: {episode_title.strip()} (data-id: {data_id})")
            
            return episodes
        
        return []
        
    except Exception as e:
        print(f"Failed to get season episodes: {e}")
        return []

def get_episode_servers(data_id: str, preferred_provider: str = "Vidcloud"):
    """Get episode servers using lobster's approach"""
    try:
        servers_url = f"{FLIXHQ_AJAX_URL}/v2/episode/servers/{data_id}"
        
        response = client.get(servers_url)
        print(f"Debug: Servers URL: {servers_url}")
        print(f"Debug: Servers response status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse like lobster: look for data-id and title in nav-item elements
            content = response.text.replace('\n', '').replace('class="nav-item"', '\nclass="nav-item"')
            
            server_pattern = re.compile(r'data-id="(\d+)"[^>]*title="([^"]*)"')
            matches = server_pattern.findall(content)
            
            servers = []
            for server_id, server_name in matches:
                servers.append({
                    'id': server_id,
                    'name': server_name.strip()
                })
                print(f"Debug: Found server: {server_name.strip()} (ID: {server_id})")
            
            # Find preferred provider like lobster does
            for server in servers:
                if preferred_provider.lower() in server['name'].lower():
                    print(f"Debug: Selected {preferred_provider} server: {server['id']}")
                    return server['id']
            
            # Fallback to first server
            if servers:
                print(f"Debug: Using fallback server: {servers[0]['id']}")
                return servers[0]['id']
        
        return None
        
    except Exception as e:
        print(f"Failed to get episode servers: {e}")
        return None

def get_embed_link(episode_id: str):
    """Get embed link from episode sources endpoint"""
    try:
        sources_url = f"{FLIXHQ_AJAX_URL}/episode/sources/{episode_id}"
        
        response = client.get(sources_url)
        print(f"Debug: Sources URL: {sources_url}")
        print(f"Debug: Sources response status: {response.status_code}")
        
        if response.status_code == 200:
            # Extract like lobster: look for "link" in JSON response
            link_match = re.search(r'"link":"([^"]*)"', response.text)
            if link_match:
                embed_link = link_match.group(1)
                print(f"Debug: Found embed link: {embed_link}")
                return embed_link
        
        return None
        
    except Exception as e:
        print(f"Failed to get embed link: {e}")
        return None

def movie():
    """Handle movie streaming"""
    global selected_media, selected_subtitles
    
    # Extract media ID from URL
    media_id_match = re.search(r'/movie/[^/]*-(\d+)', get_id.selected_url)
    if not media_id_match:
        raise RuntimeError("Could not extract media ID from URL")
    
    media_id = media_id_match.group(1)
    print(f"Debug: Movie media ID: {media_id}")
    
    # For movies, use the movie/episodes endpoint like lobster
    try:
        movie_episodes_url = f"{FLIXHQ_AJAX_URL}/movie/episodes/{media_id}"
        response = client.get(movie_episodes_url)
        
        if response.status_code == 200:
            # Extract like lobster: find href with provider name
            content = response.text.replace('\n', '').replace('class="nav-item"', '\nclass="nav-item"')
            
            # Look for Vidcloud provider first
            provider_pattern = re.compile(r'href="([^"]*)"[^>]*title="Vidcloud"')
            match = provider_pattern.search(content)
            
            if match:
                movie_page_url = FLIXHQ_BASE_URL + match.group(1)
                # Extract episode ID like lobster: -(\d+).(\d+)$ -> take the second number
                episode_match = re.search(r'-(\d+)\.(\d+)$', movie_page_url)
                if episode_match:
                    episode_id = episode_match.group(2)
                    print(f"Debug: Movie episode ID: {episode_id}")
                    
                    # Get embed link
                    embed_link = get_embed_link(episode_id)
                    if embed_link:
                        selected_media = {
                            'file': embed_link,
                            'label': 'Movie Stream',
                            'type': 'embed'
                        }
                        selected_subtitles = []
                        return
    
    except Exception as e:
        print(f"Movie processing failed: {e}")
    
    raise RuntimeError("Could not get movie stream")

def series():
    """Handle series streaming using lobster's exact approach"""
    global selected_media, selected_subtitles
    
    season = input("Enter season: ")
    episode = input("Enter episode: ")
    
    try:
        season_num = int(season)
        episode_num = int(episode)
    except ValueError:
        print("Invalid season or episode number")
        raise RuntimeError("Invalid season or episode number")
    
    # Extract media ID from URL
    media_id_match = re.search(r'/tv/[^/]*-(\d+)', get_id.selected_url)
    if not media_id_match:
        raise RuntimeError("Could not extract media ID from URL")
    
    media_id = media_id_match.group(1)
    print(f"Debug: TV media ID: {media_id}")
    
    # Step 1: Get seasons
    seasons = get_tv_seasons(media_id)
    if not seasons:
        raise RuntimeError("Could not get seasons")
    
    # Step 2: Find the target season (try exact match first, then positional)
    target_season_id = None
    for season_data in seasons:
        season_title = season_data['title'].lower()
        if f"season {season_num}" in season_title or f"s{season_num}" in season_title:
            target_season_id = season_data['id']
            break
    
    # Fallback: assume seasons are in order
    if not target_season_id and season_num <= len(seasons):
        target_season_id = seasons[season_num - 1]['id']
    
    if not target_season_id:
        raise RuntimeError(f"Could not find season {season_num}")
    
    print(f"Debug: Target season ID: {target_season_id}")
    
    # Step 3: Get episodes for this season
    episodes = get_season_episodes(target_season_id)
    if not episodes:
        raise RuntimeError(f"Could not get episodes for season {season_num}")
    
    # Step 4: Find the target episode (assume episodes are in order)
    if episode_num > len(episodes):
        raise RuntimeError(f"Episode {episode_num} not found (only {len(episodes)} episodes available)")
    
    target_episode = episodes[episode_num - 1]  # Episodes are 1-indexed
    print(f"Debug: Target episode: {target_episode['title']} (data-id: {target_episode['data_id']})")
    
    # Step 5: Get episode servers and select Vidcloud
    episode_id = get_episode_servers(target_episode['data_id'], "Vidcloud")
    if not episode_id:
        raise RuntimeError("Could not get episode server ID")
    
    # Step 6: Get embed link
    embed_link = get_embed_link(episode_id)
    if not embed_link:
        raise RuntimeError("Could not get embed link")
    
    selected_media = {
        'file': embed_link,
        'label': f'S{season_num}E{episode_num} Stream',
        'type': 'embed'
    }
    selected_subtitles = []

def get_id(query: str):
    """Search and select content"""
    selected_url = search_content(query)
    if not selected_url:
        print("No content selected")
        exit(0)
    
    get_id.selected_url = selected_url
    
    # Determine content type from URL
    if '/movie/' in selected_url:
        get_id.content_type = 'movie'
    elif '/tv/' in selected_url:
        get_id.content_type = 'series'
    else:
        get_id.content_type = 'unknown'
    
    return selected_url

def poison():
    """Choose content type"""
    if hasattr(get_id, 'content_type') and get_id.content_type in ['movie', 'series']:
        if get_id.content_type == 'movie':
            movie()
        elif get_id.content_type == 'series':
            series()
        else:
            ch = fzf_prompt(["movie", "series"])
            if ch == "movie":
                movie()
            elif ch == "series":
                series()
            else:
                exit(0)
    else:
        ch = fzf_prompt(["movie", "series"])
        if ch == "movie":
            movie()
        elif ch == "series":
            series()
        else:
            exit(0)

def determine_path() -> str:
    plt = platform.system()
    if plt == "Windows":
        return f"C://Users//{os.getenv('username')}//Downloads"
    elif plt == "Linux":
        return f"/home/{os.getlogin()}/Downloads"
    elif plt == "Darwin":
        return f"/Users/{os.getlogin()}/Downloads"
    else:
        print("[!] Make an issue for your OS.")
        exit(0)

def dlData(path: str = determine_path()):
    global selected_media
    if selected_media:
        decoded_url, subs = decode_url(selected_media['file']) 
        download(path, query, decoded_url, FLIXHQ_BASE_URL)
    else:
        print("No media selected for download")

def provideData():
    global selected_media, selected_subtitles
    if selected_media:
        decoded_url, subs = decode_url(selected_media['file'])
        play(decoded_url, query, FLIXHQ_BASE_URL, subs)
    else:
        print("No media selected for playback")

def init():
    ch = fzf_prompt(["play", "download", "exit"])
    if ch == "play":
        provideData()
    elif ch == "download":
        dlData()
    else:
        exit(0)

if len(sys.argv) == 1:
    query = input("Search: ")
    if query == "":
        print("ValueError: no query parameter provided")
        exit(0)
else:
    query = " ".join(sys.argv[1:])

get_id(query)
poison()
init()

