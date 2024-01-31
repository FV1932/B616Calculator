import requests_cache
from urllib.parse import urljoin
import pathlib
from base64 import b16decode, b16encode
import logging
import time

logger = logging.getLogger(__name__)

BASE_URL = "https://arcwiki.mcd.blue/"
SITE_CACHE = pathlib.Path("./site_cache/")


session = requests_cache.CachedSession("arcwiki_cache")

def make_throttle_hook(timeout: float = 1.0):
    def hook(response, *args, **kwargs):
        if not getattr(response, "from_cache", False):
            logger.info(f"Cache miss at {response.url}")
            time.sleep(timeout)
        return response
    return hook

session.hooks['response'].append(make_throttle_hook(1))


def get_resource(path: str, refresh: bool = False) -> str:
    full_url = urljoin(BASE_URL, path)
    res = session.get(full_url, refresh)
    if res.status_code >= 300:
        raise RuntimeError(f"Failed to get resource at {full_url}")
    return res.text
