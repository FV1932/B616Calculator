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

    def __getitem__(self, name: str):
        return self.__obj[name]

    def __setitem__(self, name: str, newval):
        self.__obj[name] = newval

    def get_cover_url(self) -> str | None:
        return self["cover_url"]