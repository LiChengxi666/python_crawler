import crawler


import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import numpy as np
import re
from fake_useragent import UserAgent
import json
from urllib.parse import urljoin
from tqdm import tqdm


# 网易云音乐url
global base_url
base_url = "https://music.163.com"


# 配置请求信息
base_headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6",
    "priority": "u=0, i",
    "referer": "https://music.163.com/",
    "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "iframe",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
}
with open("cookie.txt", "r") as f:
    cookie_str = f.read()
cookies = crawler.parse_cookies(cookie_str)


# 从三个页面（华语男歌手，华语女歌手，华语组合）中爬取歌手id）
cat_ids = {"华语男歌手": "1001", "华语女歌手": "1002", "华语组合": "1003"}
total_artist_ids = []
print(f"starting get artist id...")
for cat, cat_id in cat_ids.items():
    url = urljoin(base_url, f"discover/artist/cat?id={cat_id}")
    artists_data = crawler.get_artist_id(url=url, headers=base_headers, cookies=cookies)
    artists_data_new = artists_data.assign(cat=cat)
    total_artist_ids.append(artists_data_new)
    print(f"{cat_id} done")
    time.sleep(np.random.uniform(1, 3))
total_artist_ids = pd.concat(total_artist_ids, axis=0, ignore_index=True)
total_artist_ids.to_csv("./data/artist_ids.csv", index=False)
print("artist id done\n")


# 依据歌手id从歌手详情页获取歌手歌曲信息和歌手详情
total_songs = []
artist_details = []
print(f"starting get artist detail...")
artist_ids = list(total_artist_ids.loc[:, "id"])
for artist_id in tqdm(artist_ids):
    artist_detail, songs_urls = crawler.get_artist_detail(
        id=artist_id, headers=base_headers, cookies=cookies
    )
    total_songs.append(songs_urls)
    artist_details.append(artist_detail)
    print(f"id:{artist_id} done")
    time.sleep(np.random.uniform(0.5, 1))
    songs = pd.concat(total_songs)
    songs.to_csv("./data/songs_urls.csv", index=False)
    artists = pd.DataFrame(artist_details)
    artists.to_csv("./data/artist_details.csv", index=False)
total_songs = pd.concat(total_songs)
artist_details = pd.DataFrame(artist_details)
artist_details.to_csv("./data/artist_details.csv", index=False)
total_songs.to_csv("./data/songs_urls.csv", index=False)
print("artist detail done\n")


# 获取歌曲详细信息
gongs_information = []
print(f"starting get songs detail...")
song_ids = list(total_songs.loc[:, "id"])
for song_id in tqdm(song_ids):
    song_detail = crawler.get_songs_detail(
        id=song_id, headers=base_headers, cookies=cookies
    )
    gongs_information.append(song_detail)
    songs_inf = pd.DataFrame(gongs_information)
    songs_inf.to_csv("./data/songs_information.csv", index=False)
    print(f"id:{song_id} done")
    time.sleep(np.random.uniform(0.5, 1))
songs_information = pd.DataFrame(gongs_information)
songs_information.to_csv("./data/songs_information_new.csv", index=False)
print("songs detail done\n")
