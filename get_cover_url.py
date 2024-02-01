from cache_handler import LocalCache
import lxml.html as html
from urllib.parse import urljoin
import logging
from request_handler import get_resource

logger = logging.getLogger(__name__)

def get_cover_url(song_id: str, *, force_flush_cache = False) -> str:
    with LocalCache(song_id) as ch:
        if not force_flush_cache:
            url = ch.get_cover_url()
            if url:
                logger.info(f"Returning cover url of {song_id}: {url}")
                return url
        imagePageUrl = f"/File:Songs_{song_id}.jpg"
        res = get_resource(imagePageUrl).text
        doc_root = html.document_fromstring(res)
        link_div = doc_root.find_class("internal")[0]
        cover_url = link_div.get("href")
        ch.set_cover_url(cover_url)
        logger.info(f"Set cover url of {song_id} to {cover_url}")
    return cover_url


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    get_cover_url("tempestissimo", force_flush_cache=True)

