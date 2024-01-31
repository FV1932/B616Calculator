import requests
from cache_handler import CacheHandler


def make_cover_url(song_id: str):
    with CacheHandler(song_id) as ch:
        url = ch.get_cover_url()
        if url:
            return url
        imagePageUrl = f"https://arcwiki.mcd.blue/File:Songs_{song_id}.jpg"
        res = requests.get(imagePageUrl)
        if res.status_code >= 300:
            raise RuntimeError(
                f"Request to obtain song cover URL for {song_id} failed with {res.status_code}."
            )
        
