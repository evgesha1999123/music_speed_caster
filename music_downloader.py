import asyncio
from os import getenv
from pathlib import Path
from typing import List, AsyncIterable
from yandex_music import ClientAsync
from dotenv import load_dotenv

load_dotenv()

YA_TOKEN = getenv("YA_TOKEN")
DEFAULT_CACHE_FOLDER = Path(__file__).resolve().parent / '.YMcache'
MAX_TRACKS = 200

async def init_ym_client() -> ClientAsync:
    return await ClientAsync(token=YA_TOKEN, report_unknown_fields=False).init()

async def get_liked_tracks(client: ClientAsync, max_tracks: int = MAX_TRACKS) -> List:
    likes = await client.users_likes_tracks()
    print(likes)
    return likes[:max_tracks]

async def download_track(track_short, cache_folder: Path = DEFAULT_CACHE_FOLDER) -> Path | None:
    """Загружает один трек и возвращает путь к файлу"""
    try:
        track = track_short.track or await track_short.fetch_track_async()
        artist = track.artists[0]
        album = track.albums[0]
        
        filename = f"{artist.name}_{album.title}_{track.title}.mp3".replace(" ", "_")
        filepath = cache_folder / filename
        
        if not filepath.exists():
            filepath.parent.mkdir(parents=True, exist_ok=True)
            await track.download_async(filepath)
            print(f"Downloaded: {filepath}")
        else:
            print(f"Exists: {filepath}")
            
        return filepath
        
    except Exception as e:
        print(f"Error downloading track: {e}")

async def track_downloader(max_tracks: int = MAX_TRACKS) -> AsyncIterable[Path]:
    """Асинхронный генератор загруженных треков"""
    client = await init_ym_client()
    tracks = await get_liked_tracks(client, max_tracks)
    
    for track_short in tracks:
        filepath = await download_track(track_short)
        if filepath:
            yield filepath

async def download_and_process_tracks(callback=None):
    """Основная функция для вызова из UI"""
    downloaded_tracks = []
    
    async for track_path in track_downloader():
        downloaded_tracks.append(track_path)
        if callback:
            # Вызываем callback для обновления UI после каждой загрузки
            await callback(downloaded_tracks.copy())
    
    return downloaded_tracks

async def main():
    await download_and_process_tracks()

if __name__ == "__main__":
    asyncio.run(main())