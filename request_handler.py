import requests
from urllib.parse import urljoin
import pathlib
from base64 import b16decode, b16encode
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://arcwiki.mcd.blue/"
SITE_CACHE = pathlib.Path("./site_cache/")


def encode_directory(url_path: str) -> str:
    return b16encode(url_path.encode()).decode()


def decode_directory(local_path: str) -> str:
    return b16decode(local_path).decode()


def get_resource(path: str, force_flush_cache: bool = False) -> str:
    encoded_dir = encode_directory(path)
    local_cache_path = pathlib.Path(SITE_CACHE, encoded_dir[:2], encoded_dir)
    full_url = urljoin(BASE_URL, path)
    
    if local_cache_path.is_file() and not force_flush_cache:
        logger.info(f"Cache hit for resource at {path}")
        with open(local_cache_path, "r") as f:
            return "\n".join(f.readlines())

    logger.info(f"Cache miss for resource at {path}")
    res = requests.get(full_url)
    if res.status_code >= 300:
        raise RuntimeError(f"Failed to get resource at {full_url}")
    local_cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(local_cache_path, "w") as f:
        f.write(res.text)
    return res.text
