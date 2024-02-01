from get_cover_url import get_cover_url
from cache_handler import LocalCache
from request_handler import get_resource
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


def get_all_covers():
    with open("static/chartconstant.json", "r") as f:
        cover_urls = json.load(f)
    
    total_num = len(cover_urls)
    for idx, song_id in enumerate(cover_urls):
        with LocalCache(song_id) as ch:
            cover_url = ch.get_cover_url()
            cover = get_resource(cover_url).content
            ch.write_file("cover.jpg", cover)
            logging.info(f"{song_id} done ({idx + 1} / {total_num}).")
            # break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    get_all_covers()
