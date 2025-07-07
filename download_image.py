import numpy as np
import pandas as pd
import requests
from fake_useragent import UserAgent
from tqdm import tqdm
import logging


# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 下载歌手图片，文件名为id
artist_information = pd.read_csv("./data/artist_information.csv")
artist_image_urls = list(artist_information["image_url"])
artist_ids = list(artist_information["id"])
for artist_url, artist_id in tqdm(zip(artist_image_urls, artist_ids)):
    try:
        response = requests.get(artist_url, headers={"User-Agent": UserAgent().random})
        with open(f"./data/artist_image/{artist_id}.jpg", "wb") as file:
            file.write(response.content)
    except Exception as e:
        logger.error(f"Error getting song description: {e}")


song_information = pd.read_csv("./data/song_information.csv")
song_image_urls = list(song_information["image_url"])
song_ids = list(song_information["id"])
for song_url, song_id in tqdm(zip(song_image_urls, song_ids)):
    try:
        response = requests.get(song_url, headers={"User-Agent": UserAgent().random})
        with open(f"./data/song_image/{song_id}.jpg", "wb") as file:
            file.write(response.content)
    except Exception as e:
        logger.error(f"Error getting song description: {e}")
