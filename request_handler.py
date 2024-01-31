import requests
from urllib.parse import urljoin
from base64 import b16decode, b16encode

BASE_URL = "https://arcwiki.mcd.blue/"
SITE_CACHE = "./site_cache/"

def encode_directory(url_path: str) -> str:
    return b16encode(url_path.encode()).decode()

def decode_directory(local_path: str) -> str:
    return b16decode(local_path).decode()



