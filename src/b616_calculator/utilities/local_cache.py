import pathlib
import json


class LocalCache:
    """Handles local caches for a song.
    This actually shouldn't be used by the user.
    TODO: Write a better class that serves data from the cache or request it
    as necessary.

    N.B. NOT THREAD SAFE
    """

    LOCAL_CACHE = "./cache/"

    @staticmethod
    def getMainCachePath(song_id) -> pathlib.Path:
        return pathlib.Path(LocalCache.LOCAL_CACHE, song_id, "main.json")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        with open(self.mainPath, "w") as f:
            json.dump(self.__obj, f)

    def __init__(self, song_id: str) -> None:
        self.song_id: str = str(song_id)
        self.mainPath = LocalCache.getMainCachePath(self.song_id)
        self.mainPath.parent.mkdir(parents=True, exist_ok=True)
        if self.mainPath.is_file():
            with open(self.mainPath, "r") as f:
                self.__obj = json.load(f)
        else:
            self.__obj = {}

    def __getitem__(self, name: str):
        return self.__obj.get(name, None)

    def __setitem__(self, name: str, newval):
        self.__obj[name] = newval

    def get_cover_url(self) -> str | None:
        return self["cover_url"]
    
    def set_cover_url(self, cover_url: str):
        self["cover_url"] = cover_url
    
    def get_file(self, filename: str) -> bytes:
        return (self.mainPath.parent / filename).read_bytes()
    
    def write_file(self, filename: str, contents: bytes | str):
        if isinstance(contents, str):
            mode = "w"
        elif isinstance(contents, bytes):
            mode = "wb"
        else:
            raise TypeError("contents must be of type bytes or str")
        with open(self.mainPath.parent / filename, mode) as f:
            f.write(contents)

