import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re
from fake_useragent import UserAgent
import json
from urllib.parse import urljoin

# 获取歌手id
def get_artist_id(url, headers=None):
    """
    爬取对应页面下的歌手id，歌手名称等基本信息，并依据爬取的信息构造并存储歌手详情页的url
    """
    if headers is None:
        headers = {"User-Agent": UserAgent().random}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    artists = soup.find_all("a", class_="nm nm-icn f-thide s-fc0")
    artists_data = []
    for a in artists:
        row = {
            "href": a.get("href", None),  # 获取href属性，不存在则为None
            "name": a.get_text(strip=True),  # 获取标签内文本
        }
        artists_data.append(row)
    artists_data = pd.DataFrame(artists_data)
    return artists_data


if __name__ == "__main__":
    base_url = "https://music.163.com"
    url = urljoin(base_url, "discover/artist/cat?id=1001")
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
    artists_data = get_artist_id(url, base_headers)
    artists_data.to_csv("artists_data.csv", index=False)
