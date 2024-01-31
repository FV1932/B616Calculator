import requests
import requests_cache
from urllib.parse import urljoin
import pathlib
import logging
import time

logger = logging.getLogger(__name__)

BASE_URL = "https://arcwiki.mcd.blue/"

session = requests_cache.CachedSession("arcwiki_cache")

def get_resource(path: str, refresh: bool = False, timeout: float = 1.0) -> requests.Response:
    full_url = urljoin(BASE_URL, path)
    res = session.get(full_url, refresh)
    if not getattr(res, "from_cache", False):
        logger.info(f"Cache miss at {path}. Sleeping for {timeout} seconds")
        time.sleep(timeout)
    return res
