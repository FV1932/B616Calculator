from get_cover_url import get_cover_url
import json
import time
import logging

def main():
    with open("static/chartconstant.json", "r") as f:
        obj = json.load(f)
    for song_id in obj:
        print(f"{song_id}: {get_cover_url(song_id)}")
        # time.sleep(1)


def get_all_cover_urls():
    with open("static/chartconstant.json", "r") as f:
        obj = json.load(f)
    cover_urls = dict()
    
    for song_id in obj:
        cover_urls[song_id] = get_cover_url(song_id)
    with open("outputs/cover_urls.json", "w") as f:
        json.dump(cover_urls, f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    get_all_cover_urls()
