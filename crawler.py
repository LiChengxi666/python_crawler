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
    爬取对应页面下的歌手id，歌手名称等基本信息，并依据爬取的信息构造并存储歌手详情页的url
    """
    if headers is None:
        headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, "html.parser")
    # 获取包含歌手信息的标签
    artists = soup.find_all("a", class_="nm nm-icn f-thide s-fc0")
    artists_data = []
    # 将歌手名称和url（相对路径）进行存储
    for a in artists:
        row = {
            "href": a.get("href", None),
            "name": a.get_text(strip=True),
        }
        artists_data.append(row)
    artists_data = pd.DataFrame(artists_data)

    return artists_data


# 获取歌手详情页信息
def get_artist_detail(url, headers=None, cookies=None):
    """
    爬取歌手详情页信息, 获取歌手简介，歌手图片，歌曲url等；
    其中：歌手基本信息，包含姓名，简介，图片url等返回一个字典；
    其下默认展示在首页的歌曲（100首）的url返回一个表格
    """
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
    # 获取歌曲url，并将相对路径拼接为绝对路径
    songs_urls = []
    songs = soup.find_all("a", href=re.compile(r"/song\?id=\d+$"))
    for song in songs:
        songs_url = urljoin(base_url, song.get("href"))
        row = {
            "artist": name,
            "name": song.get_text(strip=True),
            "href": songs_url,
        }
        songs_urls.append(row)
    songs_urls = pd.DataFrame(songs_urls)
    return artist_infomation, songs_urls


if __name__ == "__main__":

    print(0)
