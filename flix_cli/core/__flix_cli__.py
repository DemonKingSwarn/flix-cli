#!/usr/bin/env python3

import os
import platform

import httpx
import regex as re
from fzf import fzf_prompt

from .__version__ import __core__
from .utils.__cast__ import cast
from .utils.__decryptor__ import decrypt_stream_url
from .utils.__downloader__ import download
from .utils.__player__ import play

try:
    import orjson as json  # noqa: F401
except ImportError:
    pass

import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup

headers = {
    "User-Agent": f"flix-cli/{__core__}",
    "Referer": "https://flixhq.to/",
    "X-Requested-With": "XMLHttpRequest",
}

client = httpx.Client(headers=headers, follow_redirects=True, timeout=None)

FLIXHQ_BASE_URL = "https://flixhq.to"
FLIXHQ_SEARCH_URL = f"{FLIXHQ_BASE_URL}/search"
FLIXHQ_AJAX_URL = f"{FLIXHQ_BASE_URL}/ajax"
DECODER = "https://dec.eatmynerds.live"

selected_media = None
selected_subtitles = []


def parse_episode_range(episode_input: str) -> list[int] | None:
    """Parse episode input to handle ranges like '5-7' or single episodes like '5'"""
    episode_input = episode_input.strip()
    if "-" in episode_input:
        try:
            start, end = episode_input.split("-", 1)
            start_ep = int(start.strip())
            end_ep = int(end.strip())
            if start_ep > end_ep:
                raise ValueError("Start episode cannot be greater than end episode")
            return list(range(start_ep, end_ep + 1))
        except ValueError as e:
            print(f"Invalid episode range format: {e}")
            return None
    else:
        try:
            single_ep = int(episode_input)
            return [single_ep]
        except ValueError:
            print("Invalid episode number")
            return None


def search_content(query: str):
    """Search for content on flixhq.to"""
    try:
        search_params = query.replace(" ", "-")
        response = client.get(f"{FLIXHQ_SEARCH_URL}/{search_params}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="flw-item")
        if not items:
            print("No results found")
            return None
        results = []
        urls = []
        for i, item in enumerate(items[:10]):
            poster_link = item.find("div", class_="film-poster")
            detail_section = item.find("div", class_="film-detail")
            if poster_link and detail_section:
                link_elem = poster_link.find("a")
                title_elem = detail_section.find("h2", class_="film-name")
                if link_elem and title_elem:
                    href = link_elem.get("href", "")
                    title_link = title_elem.find("a")
                    title = (
                        title_link.get("title", "Unknown Title") if title_link else "Unknown Title"
                    )
                    info_elem = detail_section.find("div", class_="fd-infor")
                    year = ""
                    content_type = ""
                    if info_elem:
                        spans = info_elem.find_all("span")
                        if spans:
                            year = spans[0].text.strip() if spans else ""
                            if len(spans) > 1:
                                content_type = spans[1].text.strip()
                    display_title = f"{i + 1}. {title}"
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
    try:
        seasons_url = f"{FLIXHQ_AJAX_URL}/v2/tv/seasons/{media_id}"
        response = client.get(seasons_url)
        if response.status_code == 200:
            season_pattern = re.compile(r'href="[^"]*-(\d+)"[^>]*>([^<]*)</a>')
            matches = season_pattern.findall(response.text)
            seasons = []
            for season_id, season_title in matches:
                seasons.append({"id": season_id, "title": season_title.strip()})
            return seasons
        return []
    except Exception as e:
        print(f"Failed to get TV seasons: {e}")
        return []


def get_season_episodes(season_id: str):
    try:
        episodes_url = f"{FLIXHQ_AJAX_URL}/v2/season/episodes/{season_id}"
        response = client.get(episodes_url)
        if response.status_code == 200:
            content = response.text.replace("\n", "").replace(
                'class="nav-item"', '\nclass="nav-item"'
            )
            episode_pattern = re.compile(r'data-id="(\d+)"[^>]*title="([^"]*)"')
            matches = episode_pattern.findall(content)
            episodes = []
            for data_id, episode_title in matches:
                episodes.append({"data_id": data_id, "title": episode_title.strip()})
            return episodes
        return []
    except Exception as e:
        print(f"Failed to get season episodes: {e}")
        return []


def get_episode_servers(data_id: str, preferred_provider: str = "Vidcloud"):
    try:
        servers_url = f"{FLIXHQ_AJAX_URL}/v2/episode/servers/{data_id}"
        response = client.get(servers_url)
        if response.status_code == 200:
            content = response.text.replace("\n", "").replace(
                'class="nav-item"', '\nclass="nav-item"'
            )
            server_pattern = re.compile(r'data-id="(\d+)"[^>]*title="([^"]*)"')
            matches = server_pattern.findall(content)
            servers = []
            for server_id, server_name in matches:
                servers.append({"id": server_id, "name": server_name.strip()})
            for server in servers:
                if preferred_provider.lower() in server["name"].lower():
                    return server["id"]
            if servers:
                return servers[0]["id"]
        return None
    except Exception as e:
        print(f"Failed to get episode servers: {e}")
        return None


def get_embed_link(episode_id: str):
    try:
        sources_url = f"{FLIXHQ_AJAX_URL}/episode/sources/{episode_id}"
        response = client.get(sources_url)
        if response.status_code == 200:
            link_match = re.search(r'"link":"([^"]*)"', response.text)
            if link_match:
                embed_link = link_match.group(1)
                return embed_link
        return None
    except Exception as e:
        print(f"Failed to get embed link: {e}")
        return None


def get_episode_data(target_episode, season_num, episode_num):
    """Get stream data for a single episode"""
    episode_id = get_episode_servers(target_episode["data_id"], "Vidcloud")
    if not episode_id:
        print(f"Warning: Could not get server ID for episode {episode_num}")
        return None
    embed_link = get_embed_link(episode_id)
    if not embed_link:
        print(f"Warning: Could not get embed link for episode {episode_num}")
        return None
    return {
        "file": embed_link,
        "label": f"S{season_num}E{episode_num} - {target_episode['title']}",
        "type": "embed",
        "season": season_num,
        "episode": episode_num,
    }


def movie():
    """Handle movie streaming"""
    global selected_media, selected_subtitles
    media_id_match = re.search(r"/movie/[^/]*-(\d+)", get_id.selected_url)
    if not media_id_match:
        raise RuntimeError("Could not extract media ID from URL")
    media_id = media_id_match.group(1)
    try:
        movie_episodes_url = f"{FLIXHQ_AJAX_URL}/movie/episodes/{media_id}"
        response = client.get(movie_episodes_url)
        if response.status_code == 200:
            content = response.text.replace("\n", "").replace(
                'class="nav-item"', '\nclass="nav-item"'
            )
            provider_pattern = re.compile(r'href="([^"]*)"[^>]*title="Vidcloud"')
            match = provider_pattern.search(content)
            if match:
                movie_page_url = FLIXHQ_BASE_URL + match.group(1)
                episode_match = re.search(r"-(\d+)\.(\d+)$", movie_page_url)
                if episode_match:
                    episode_id = episode_match.group(2)
                    embed_link = get_embed_link(episode_id)
                    if embed_link:
                        selected_media = [
                            {"file": embed_link, "label": "Movie Stream", "type": "embed"}
                        ]
                        selected_subtitles = []
                        return
    except Exception as e:
        print(f"Movie processing failed: {e}")
    raise RuntimeError("Could not get movie stream")


def series():
    """Handle series streaming with episode range support"""
    global selected_media, selected_subtitles
    season = input("Enter season: ")
    episode_input = input("Enter episode (e.g., '5' or '5-7' for range): ")
    try:
        season_num = int(season)
    except ValueError:
        print("Invalid season number")
        raise RuntimeError("Invalid season number")
    episode_numbers = parse_episode_range(episode_input)
    if not episode_numbers:
        raise RuntimeError("Invalid episode input")
    media_id_match = re.search(r"/tv/[^/]*-(\d+)", get_id.selected_url)
    if not media_id_match:
        raise RuntimeError("Could not extract media ID from URL")
    media_id = media_id_match.group(1)
    seasons = get_tv_seasons(media_id)
    if not seasons:
        raise RuntimeError("Could not get seasons")
    target_season_id = None
    for season_data in seasons:
        season_title = season_data["title"].lower()
        if f"season {season_num}" in season_title or f"s{season_num}" in season_title:
            target_season_id = season_data["id"]
            break
    if not target_season_id and season_num <= len(seasons):
        target_season_id = seasons[season_num - 1]["id"]
    if not target_season_id:
        raise RuntimeError(f"Could not find season {season_num}")
    episodes = get_season_episodes(target_season_id)
    if not episodes:
        raise RuntimeError(f"Could not get episodes for season {season_num}")
    max_episode = len(episodes)
    for ep_num in episode_numbers:
        if ep_num > max_episode:
            raise RuntimeError(
                f"Episode {ep_num} not found (only {max_episode} episodes available)"
            )
    episode_data_list = []
    failed_episodes = []
    for episode_num in episode_numbers:
        target_episode = episodes[episode_num - 1]
        episode_data = get_episode_data(target_episode, season_num, episode_num)
        if episode_data:
            episode_data_list.append(episode_data)
        else:
            failed_episodes.append(episode_num)
    if failed_episodes:
        print(f"Warning: Failed to get data for episodes: {failed_episodes}")
    if not episode_data_list:
        raise RuntimeError("Could not get data for any episodes")
    selected_media = episode_data_list
    selected_subtitles = []
    if len(episode_numbers) > 1:
        print(f"Successfully prepared {len(episode_data_list)} episodes for streaming/download")
    else:
        print(f"Successfully prepared episode {episode_numbers[0]} for streaming/download")


def get_id(query: str):
    """Search and select content"""
    selected_url = search_content(query)
    if not selected_url:
        print("No content selected")
        exit(0)
    get_id.selected_url = selected_url
    if "/movie/" in selected_url:
        get_id.content_type = "movie"
    elif "/tv/" in selected_url:
        get_id.content_type = "series"
    else:
        get_id.content_type = "unknown"
    return selected_url


def poison():
    """Choose content type"""
    if hasattr(get_id, "content_type") and get_id.content_type in ["movie", "series"]:
        if get_id.content_type == "movie":
            movie()
        elif get_id.content_type == "series":
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
    elif plt == "Linux" or plt == "FreeBSD":
        return f"/home/{os.getlogin()}/Downloads"
    elif plt == "Darwin":
        return f"/Users/{os.getlogin()}/Downloads"
    else:
        print("[!] Make an issue for your OS.")
        exit(0)


def dlData(path: str = determine_path()):
    """Download media with support for episode ranges"""
    global selected_media
    if selected_media:
        episodes_to_download = (
            selected_media if isinstance(selected_media, list) else [selected_media]
        )
        print(f"Starting download of {len(episodes_to_download)} episode(s)...")
        for i, episode_data in enumerate(episodes_to_download, 1):
            print(f"\nDownloading episode {i}/{len(episodes_to_download)}: {episode_data['label']}")
            try:
                decoded_url, subs = decrypt_stream_url(episode_data["file"])
                if "season" in episode_data and "episode" in episode_data:
                    episode_query = (
                        f"{query}_S{episode_data['season']:02d}E{episode_data['episode']:02d}"
                    )
                else:
                    episode_query = f"{query}_Episode_{i}"
                download(path, episode_query, decoded_url, FLIXHQ_BASE_URL, subs)
                print(f"Successfully downloaded: {episode_data['label']}")
            except Exception as e:
                print(f"Failed to download episode {i}: {e}")
                continue
        print(f"\nDownload completed for {len(episodes_to_download)} episode(s)")
    else:
        print("No media selected for download")


def provideData(play_type: str) -> None:
    """Play media with support for episode ranges"""
    global selected_media, selected_subtitles
    if selected_media:
        episodes_to_play = selected_media if isinstance(selected_media, list) else [selected_media]
        print(f"Starting playback of {len(episodes_to_play)} episode(s)...")
        for i, episode_data in enumerate(episodes_to_play, 1):
            print(f"\nPlaying episode {i}/{len(episodes_to_play)}: {episode_data['label']}")
            try:
                decoded_url, subs = decrypt_stream_url(episode_data["file"])

                if "episode_title" in episode_data:
                    episode_title = episode_data["episode_title"]
                elif "movie_title" in episode_data:
                    episode_title = episode_data["movie_title"]
                else:
                    episode_title = episode_data["label"]

                if play_type == "play":
                    play(decoded_url, episode_title, FLIXHQ_BASE_URL, subs)
                elif play_type == "cast":
                    cast(decoded_url, subs)
                if len(episodes_to_play) > 1 and i < len(episodes_to_play):
                    continue_choice = input("\nContinue to next episode? (y/n): ").lower().strip()
                    if continue_choice not in ["y", "yes", ""]:
                        print("Stopping playback")
                        break
            except Exception as e:
                print(f"Failed to play episode {i}: {e}")
                if len(episodes_to_play) > 1:
                    continue_choice = input("\nSkip to next episode? (y/n): ").lower().strip()
                    if continue_choice not in ["y", "yes", ""]:
                        print("Stopping playback")
                        break
                else:
                    break
    else:
        print("No media selected for playback")


def init() -> None:
    ch = fzf_prompt(["play", "download", "chromecaast", "exit"])
    if ch == "play":
        provideData("play")
    elif ch == "download":
        dlData()
    elif ch == "chromecast":
        provideData("cast")
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
