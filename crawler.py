import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re
from fake_useragent import UserAgent
import json
from urllib.parse import urljoin


# 网易云音乐url
global base_url
base_url = "https://music.163.com"


# 解析cookie，将字符串转变为字典
def parse_cookies(cookie_str: str):
    """
    将cookie字符串转为字典
    :param cookie_str:
    :return:
    """
    cookies = {}
    for cookie in cookie_str.split(";"):
        key, value = cookie.split("=", 1)
        cookies[key] = value
    return cookies


# 获取歌手id
def get_artist_id(url, headers=None, cookies=None):
    """
    爬取对应页面下的歌手id，歌手名称等基本信息
    """
    if headers is None:
        headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")
    # 获取包含歌手信息的标签
    artists = soup.find_all("a", class_="nm nm-icn f-thide s-fc0")
    artists_data = []
    # 将歌手名称和id进行存储
    for a in artists:
        artist_url = a.get("href", None)
        artist_id = re.search(r"id=(\d+)", artist_url).group(1)
        row = {
            "name": a.get_text(strip=True),
            "id": artist_id,
        }
        artists_data.append(row)
    artists_data = pd.DataFrame(artists_data)
    return artists_data


# 获取歌手详情页信息
def get_artist_detail(id, headers=None, cookies=None):
    """
    爬取歌手详情页信息, 获取歌手简介，歌手图片，歌曲id等；
    其中：歌手基本信息，包含姓名，简介，图片url，等返回一个字典；
    其下默认展示在首页的歌曲（100首）的url返回一个表格
    """
    url = urljoin(base_url, f"artist?id={id}")
    if headers is None:
        headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")
    # 获取并整合歌手基本信息
    name = soup.find("h2", id="artist-name").get_text()
    image_url = soup.find_all("meta", property="og:image")[0].get("content")
    abstract = soup.find("meta", property="og:abstract").get("content")
    artist_infomation = {
        "name": name,
        "image_url": image_url,
        "abstract": abstract,
        "url": url,
    }
    # 获取歌曲id
    songs_urls = []
    songs = soup.find_all("a", href=re.compile(r"/song\?id=\d+$"))
    for song in songs:
        song_url = urljoin(base_url, song.get("href"))
        song_id = re.search(r"id=(\d+)", song_url).group(1)
        row = {
            "artist": name,
            "name": song.get_text(strip=True),
            "href": song_id,
        }
        songs_urls.append(row)
    songs_urls = pd.DataFrame(songs_urls)
    return artist_infomation, songs_urls


if __name__ == "__main__":

    print(0)
