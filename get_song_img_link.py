import requests
from cache_handler import CacheHandler
import lxml.html as html
from urllib.parse import urljoin
import logging

BASE_URL = "https://arcwiki.mcd.blue/"


def make_cover_url(song_id: str):
    with CacheHandler(song_id) as ch:
        url = ch.get_cover_url()
        if url:
            return url
        imagePageUrl = f"/File:Songs_{song_id}.jpg"
        res = requests.get(urljoin(BASE_URL, url=imagePageUrl))
        if res.status_code >= 300:
            raise RuntimeError(
                f"Request to obtain song cover URL for {song_id} failed with {res.status_code}."
            )
        doc_root = html.document_fromstring(res.text)
        link_div = doc_root.find_class("internal")[0]
        cover_url = link_div.get("href")
        ch.set_cover_url(cover_url)
        logging.info(f"Set cover url of {song_id} to {cover_url}")


if __name__ == "__main__":
    make_cover_url("tempestissimo")

