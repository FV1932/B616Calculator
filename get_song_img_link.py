from typing import Any
import requests
import lxml.html as html
import os
import pathlib
import json


class CacheHandler:
    """Handles local caches for a song

    N.B. NOT THREAD SAFE
    """

    LOCAL_CACHE = "./cache/"

    @staticmethod
    def getMainCachePath(song_id) -> pathlib.Path:
        return pathlib.Path(CacheHandler.LOCAL_CACHE, song_id, "main.json")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.mainPath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.mainPath, "w") as f:
            json.dump(self.__obj, f)

    def __init__(self, song_id: str) -> None:
        self.song_id: str = str(song_id)
        self.mainPath = CacheHandler.getMainCachePath(self.song_id)
        if self.mainPath.is_file():
            with open(self.mainPath, "r") as f:
                self.__obj = json.load(f)
        else:
            self.__obj = {}

    def __getitem__(self, name: str) -> Any:
        return self.__obj[name]

    def __setitem__(self, name: str, newval):
        self.__obj[name] = newval

    def get_cover_url(self) -> str | None:
        return self["cover_url"]


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
        
