from os import getenv
from dotenv import load_dotenv
from yandex_music import Client
from yandex_music.exceptions import NotFoundError

from typing import List
from pathlib import Path


load_dotenv()

YA_TOKEN = getenv("YA_TOKEN")
DEFAULT_CACHE_FOLDER = Path(__file__).resolve().parent / '.YMcache'

MAX_TRACKS = 20

def init_YM_client() -> Client:
    client = Client(token=YA_TOKEN, report_unknown_fields=False).init()
    return client

def parse_tracks_from_playlist(client:Client) -> Client:
    likes_playlists = client.users_likes_tracks()
    tracks = likes_playlists[:MAX_TRACKS]
    return tracks

def download_tracks():

    load_dotenv()

    YA_TOKEN = getenv("YA_TOKEN")
    DEFAULT_CACHE_FOLDER = Path(__file__).resolve().parent / '.YMcache'
    MAX_TRACKS = 10

    client = init_YM_client()
    tracks = parse_tracks_from_playlist(client)
    ym_track_list = []

    for i, short_track in enumerate(tracks):
        try:
            track = short_track.track if short_track.track else short_track.fetchTrack()

            artist_name = track.artists[0].name
            artist_id = track.artists[0].id
            album_title = track.albums[0].title
            album_id = track.albums[0].id

            artist_dir = Path(f'{artist_name}_{artist_id}')
            album_dir = Path(f'{album_title}_{album_id}')
            file_path = DEFAULT_CACHE_FOLDER / f'{artist_name}_{album_title}_{track.title}.mp3'.replace(" ", "_")

            #print(f"{artist_dir} | {album_dir} | {file_path}")

            if not file_path.exists():
                download_status = f"Downloading: {file_path}"
                print(download_status)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    track.download(file_path)
                except Exception as error:
                    download_status = f"Error: {error}"
                    print(download_status)
            else:
                download_status = f"Track: {file_path} alredy exist, skipping"
                print(download_status)

            ym_track_list.append(file_path)

        except Exception as error:
            download_status = f"Error: {error}"
    return ym_track_list

if __name__ == "__main__":

    client = init_YM_client()

    tracks = parse_tracks_from_playlist(client)

    ym_track_list = download_tracks()
    print(ym_track_list)