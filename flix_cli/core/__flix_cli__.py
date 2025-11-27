#!/usr/bin/env python3

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# ruff: noqa: UP035 - allow using typing.List
from typing import Annotated, List, Optional, Self, overload
from urllib.parse import urljoin

import httpx
import regex as re
import typer
from bs4 import BeautifulSoup
from fzf import fzf_prompt
from platformdirs import user_downloads_path

from .__version__ import __core__
from .utils.__cast__ import cast
from .utils.__decryptor__ import decrypt_stream_url
from .utils.__downloader__ import download
from .utils.__player__ import play

FLIXHQ_BASE_URL = "https://flixhq.to"
FLIXHQ_SEARCH_URL = f"{FLIXHQ_BASE_URL}/search"
FLIXHQ_AJAX_URL = f"{FLIXHQ_BASE_URL}/ajax"
DECODER = "https://dec.eatmynerds.live"


class Action(str, Enum):
    PLAY = "play"
    DOWNLOAD = "download"
    CAST = "cast"


class MediaType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"


class EpisodeRange(Sequence[int]):
    def __init__(self, ep_range: range) -> None:
        self.range = ep_range

    @classmethod
    def from_str(cls, ep_input: str) -> Self:
        """Parse episode input to handle ranges like '5-7' or single episodes like '5'"""
        ep_input = ep_input.strip()

        try:
            if "-" in ep_input:
                start, end = ep_input.split("-", 1)
                start_ep = int(start.strip())
                end_ep = int(end.strip())

                if start_ep > end_ep:
                    start_ep, end_ep = end_ep, start_ep

                return cls(range(start_ep, end_ep + 1))
            else:
                ep = int(ep_input)
                return cls(range(ep, ep + 1))

        except ValueError:
            raise typer.BadParameter(
                "Invalid episode/range, input must be a number or range in the form <num>-<num>"
            )

    def __iter__(self) -> Iterator[int]:
        return iter(self.range)

    def __len__(self) -> int:
        return len(self.range)

    @overload
    def __getitem__(self, i: int) -> int: ...

    @overload
    def __getitem__(self, i: slice) -> Self: ...

    def __getitem__(self, i: int | slice) -> int | Self:
        if isinstance(i, slice):
            return self.__class__(self.range[i])
        return self.range[i]


@dataclass
class Context:
    client: httpx.Client

    query: str | None = None
    url: str | None = None
    title: str | None = None
    content_type: MediaType | None = None

    season: int | None = None
    episodes: EpisodeRange | None = None

    selected_media: list[dict[str, str | int | None]] | None = None
    selected_subtitles: list[str] = field(default_factory=list)

    dl_path: Path = user_downloads_path()
    play_type: Action | None = None


def search_content(query: str, client: httpx.Client):
    """Search for content on flixhq.to"""
    try:
        search_params = query.replace(" ", "-")
        response = client.get(f"{FLIXHQ_SEARCH_URL}/{search_params}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("div", class_="flw-item")

        if not items:
            raise RuntimeError("No results found for query")

        results: list[str] = []
        urls: list[str] = []
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
            raise RuntimeError("No results found for query")

        selected = fzf_prompt(results)
        if not selected:
            print("No media selected, exiting")
            exit(0)

        selected_index = int(selected[0]) - 1
        return urls[selected_index], results[selected_index].partition(". ")[-1]

    except Exception as e:
        err_msg = f"Search failed: {e}"
        raise RuntimeError(err_msg)


def get_tv_seasons(media_id: str, client: httpx.Client) -> list[dict[str, str]]:
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


def get_season_episodes(season_id: str, client: httpx.Client):
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


def get_episode_servers(data_id: str, client: httpx.Client, preferred_provider: str = "Vidcloud"):
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


def get_embed_link(episode_id: str, client: httpx.Client) -> str | None:
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


def get_episode_data(
    target_episode, season_num: int, episode_num: int, client: httpx.Client
) -> dict[str, str | int | None] | None:
    """Get stream data for a single episode"""

    episode_id = get_episode_servers(target_episode["data_id"], client, "Vidcloud")
    if episode_id is None:
        print(f"Warning: Could not get server ID for episode {episode_num}")
        return None

    embed_link = get_embed_link(episode_id, client)
    if embed_link is None:
        print(f"Warning: Could not get embed link for episode {episode_num}")
        return None

    return {
        "file": embed_link,
        "label": f"S{season_num}E{episode_num} - {target_episode['title']}",
        "type": "embed",
        "season": season_num,
        "episode": episode_num,
    }


def movie(ctx: Context):
    """Handle movie streaming"""
    assert ctx.url is not None
    media_id_match = re.search(r"/movie/[^/]*-(\d+)", ctx.url)
    if not media_id_match:
        raise RuntimeError("Could not extract media ID from URL")
    media_id = media_id_match.group(1)

    try:
        movie_episodes_url = f"{FLIXHQ_AJAX_URL}/movie/episodes/{media_id}"
        response = ctx.client.get(movie_episodes_url)

        if response.status_code != 200:
            raise RuntimeError("Failed to get media url from server")

        content = response.text.replace("\n", "").replace('class="nav-item"', '\nclass="nav-item"')

        provider_pattern = re.compile(r'href="([^"]*)"[^>]*title="Vidcloud"')
        provider_match = provider_pattern.search(content)

        if not provider_match:
            raise RuntimeError("Failed to find provider for media")

        movie_page_url = FLIXHQ_BASE_URL + provider_match.group(1)
        episode_match = re.search(r"-(\d+)\.(\d+)$", movie_page_url)

        if not episode_match:
            raise RuntimeError("Failed to find provider for media")

        episode_id = episode_match.group(2)
        embed_link = get_embed_link(episode_id, ctx.client)

        if not embed_link:
            raise RuntimeError("Failed to find provider for media")

        ctx.selected_media = [{"file": embed_link, "label": ctx.query, "type": "embed"}]
        ctx.selected_subtitles = []
        return

    except Exception as e:
        print(f"Movie processing failed: {e}")
        exit(1)


def series(ctx: Context):
    """Handle series streaming with episode range support"""
    if ctx.season is None:
        ctx.season = typer.prompt("Enter season", type=int)
    if ctx.episodes is None:
        ctx.episodes = typer.prompt(
            "Enter episode (e.g., '5' or '5-7' for range)", type=EpisodeRange.from_str
        )

    assert ctx.season is not None
    assert ctx.episodes is not None
    assert ctx.url is not None

    media_id_match = re.search(r"/tv/[^/]*-(\d+)", ctx.url)
    if not media_id_match:
        raise RuntimeError("Could not extract media ID from URL")

    media_id = media_id_match.group(1)
    seasons = get_tv_seasons(media_id, ctx.client)
    if not seasons:
        raise RuntimeError("Could not get seasons")

    target_season_id = None
    for season_data in seasons:
        season_title = season_data["title"].lower()
        if f"season {ctx.season}" in season_title or f"s{ctx.season}" in season_title:
            target_season_id = season_data["id"]
            break

    if not target_season_id and ctx.season <= len(seasons):
        target_season_id = seasons[ctx.season - 1]["id"]

    if not target_season_id:
        raise RuntimeError(f"Could not find season {ctx.season}")

    episodes = get_season_episodes(target_season_id, ctx.client)
    if not episodes:
        raise RuntimeError(f"Could not get episodes for season {ctx.season}")

    max_episode = len(episodes)
    for ep_num in ctx.episodes:
        if ep_num > max_episode:
            err_msg = f"Episode {ep_num} not found (only {max_episode} episodes available)"
            raise RuntimeError(err_msg)

    episode_data_list = []
    failed_episodes = []
    for episode_num in ctx.episodes:
        target_episode = episodes[episode_num - 1]
        episode_data = get_episode_data(target_episode, ctx.season, episode_num, ctx.client)
        if episode_data:
            episode_data_list.append(episode_data)
        else:
            failed_episodes.append(episode_num)

    if not episode_data_list:
        raise RuntimeError("Could not get data for any episodes")

    if failed_episodes:
        print(f"Warning: Failed to get data for episodes: {failed_episodes}")

    ctx.selected_media = episode_data_list
    ctx.selected_subtitles = []

    if len(ctx.episodes) > 1:
        print(f"Successfully prepared {len(episode_data_list)} episodes for streaming/download")
    else:
        print(f"Successfully prepared episode {ctx.episodes[0]} for streaming/download")


def get_id(ctx: Context) -> tuple[str, str, MediaType | None]:
    """Search and select content"""
    assert ctx.query is not None
    selected_url, title = search_content(ctx.query, ctx.client)

    if "/movie/" in selected_url:
        content_type = MediaType.MOVIE
    elif "/tv/" in selected_url:
        content_type = MediaType.SERIES
    else:
        content_type = None
    return (selected_url, title, content_type)


def get_content_type(ctx: Context):
    """Choose content type"""
    if ctx.content_type is None:
        choice = fzf_prompt(["movie", "series"])
        if choice == "movie":
            return MediaType.MOVIE
        elif choice == "series":
            return MediaType.SERIES
        else:
            exit(0)


def dl_data(ctx: Context) -> None:
    """Download media with support for episode ranges"""
    if ctx.selected_media:
        episodes_to_download = (
            ctx.selected_media if isinstance(ctx.selected_media, list) else [ctx.selected_media]
        )
        print(f"Starting download of {len(episodes_to_download)} episode(s)...")
        for i, episode_data in enumerate(episodes_to_download, 1):
            print(f"\nDownloading episode {i}/{len(episodes_to_download)}: {episode_data['label']}")
            try:
                decoded_url, subs = decrypt_stream_url(episode_data["file"])
                subs = subs if subs else []
                if "season" in episode_data and "episode" in episode_data:
                    episode_query = (
                        f"{ctx.query}_S{episode_data['season']:02d}E{episode_data['episode']:02d}"
                    )
                else:
                    episode_query = f"{ctx.query}_Episode_{i}"

                if decoded_url is None:
                    raise RuntimeError("unable to find url for episode")

                download(ctx.dl_path, episode_query, decoded_url, FLIXHQ_BASE_URL, subs)
                print(f"Successfully downloaded: {episode_data['label']}")
            except Exception as e:
                print(f"Failed to download episode {i}: {e}")
                continue
        print(f"\nDownload completed for {len(episodes_to_download)} episode(s)")
    else:
        print("No media selected for download")


def provide_data(ctx: Context) -> None:
    """Play media with support for episode ranges"""
    if ctx.selected_media:
        episodes_to_play = (
            ctx.selected_media if isinstance(ctx.selected_media, list) else [ctx.selected_media]
        )
        if ctx.content_type == MediaType.MOVIE:
            print(f"Starting playback of {ctx.title}...")
        else:
            print(f"Starting playback of {len(episodes_to_play)} episode(s)...")
        for i, episode_data in enumerate(episodes_to_play, 1):
            if ctx.content_type == MediaType.SERIES:
                print(f"\nPlaying episode {i}/{len(episodes_to_play)}: {episode_data['label']}")
            try:
                decoded_url, subs = decrypt_stream_url(episode_data["file"])
                if decoded_url is None:
                    raise RuntimeError(f"Failed to get url for episode {i}")
                subs = subs if subs else []

                if "episode_title" in episode_data:
                    episode_title = episode_data["episode_title"]
                elif "movie_title" in episode_data:
                    episode_title = episode_data["movie_title"]
                else:
                    episode_title = episode_data["label"]

                if ctx.play_type == "play":
                    play(decoded_url, episode_title, FLIXHQ_BASE_URL, subs)
                elif ctx.play_type == "cast":
                    cast(decoded_url, subs)
                if len(episodes_to_play) > 1 and i < len(episodes_to_play):
                    continue_choice = typer.confirm("Continue to next episode?")
                    if not continue_choice:
                        print("Stopping playback")
                        break
            except Exception as e:
                print(f"Failed to play episode {i}: {e}")
                if len(episodes_to_play) > 1:
                    continue_choice = typer.confirm("Continue to next episode?")
                    if not continue_choice:
                        print("Stopping playback")
                        break
                else:
                    break
    else:
        print("No media selected for playback")


app = typer.Typer()


# ruff: noqa: UP045 - allow using Optional[T] instead T | None
# ruff: noqa: UP006 - allow using typing.List
@app.command()
def main(
    query: Annotated[Optional[List[str]], typer.Argument(help="The name to search for")] = None,
    action: Annotated[
        Action,
        typer.Option(
            "--action",
            "-a",
            help="Type of playback",
        ),
    ] = Action.PLAY,
    season: Annotated[
        Optional[int], typer.Option("--season", "-s", help="Specify season number")
    ] = None,
    episodes: Annotated[
        Optional[EpisodeRange],
        typer.Option(
            "--episodes",
            "-e",
            help="Specify episode/range of episodes to download",
            parser=EpisodeRange.from_str,
        ),
    ] = None,
):
    headers = {
        "User-Agent": f"flix-cli/{__core__}",
        "Referer": "https://flixhq.to/",
        "X-Requested-With": "XMLHttpRequest",
    }
    client = httpx.Client(headers=headers, follow_redirects=True, timeout=None)

    ctx = Context(client=client)

    if query is None:
        ctx.query = typer.prompt("Search")
    else:
        ctx.query = " ".join(query)

    ctx.play_type = action
    ctx.url, ctx.title, ctx.content_type = get_id(ctx)

    if ctx.content_type is None:
        get_content_type(ctx)

    if ctx.content_type == MediaType.MOVIE:
        movie(ctx)
    else:
        if ctx.content_type != MediaType.SERIES:
            if any((season, episodes)):
                print("Warning: content type is not 'series', ignoring season/episode parameters")
        else:
            if episodes:
                ctx.episodes = episodes
            if season:
                ctx.season = season

        series(ctx)

    if action in ("play", "cast"):
        provide_data(ctx)
    elif action == "download":
        dl_data(ctx)
