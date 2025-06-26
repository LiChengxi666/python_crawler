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


# 获取歌手id
def get_artist_id(url, headers=None, cookies=None):
    '''
    爬取对应页面下的歌手id，歌手名称等基本信息，并依据爬取的信息构造并存储歌手详情页的url
    '''
    if headers is None:
        headers = {'User-Agent': UserAgent().random}
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 获取包含歌手信息的标签
    artists = soup.find_all('a', class_='nm nm-icn f-thide s-fc0')
    artists_data = []
    # 将歌手名称和url（相对路径）进行存储
    for a in artists:
        row = {
            'href': a.get('href', None),  
            'name': a.get_text(strip=True),  
        }
        artists_data.append(row)
    artists_data = pd.DataFrame(artists_data)
    
    return artists_data


# 获取歌手详情页信息
def get_artist_detail(url, headers=None, cookies=None):
    '''
    爬取歌手详情页信息, 获取歌手简介，歌手图片，歌曲url等；
    其中：歌手基本信息，包含姓名，简介，图片url等返回一个字典；
    其下默认展示在首页的歌曲（100首）的url返回一个表格
    '''
    if headers is None:
        headers = {'User-Agent': UserAgent().random}
    response = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 获取并整合歌手基本信息
    name = soup.find('h2', id="artist-name").get_text()
    image_url = soup.find_all('meta', property="og:image")[0].get('content')
    abstract = soup.find('meta', property="og:abstract").get('content')
    artist_infomation = {
        'name': name,
        'image_url': image_url,
        'abstract': abstract,
        'url': url,
    }
    # 获取歌曲url，并将相对路径拼接为绝对路径
    songs_urls = []
    songs = soup.find_all('a', href = re.compile(r"/song\?id=\d+$"))
    for song in songs:
        songs_url = urljoin(base_url, song.get('href'))
        row = {
            'artist': name,
            'name': song.get_text(strip=True),  
            'href': songs_url,  
        }
        songs_urls.append(row)
    songs_urls = pd.DataFrame(songs_urls)
    return artist_infomation, songs_urls

if __name__ == '__main__':
    url = urljoin(base_url, 'discover/artist/cat?id=1001')
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
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }
    # 测试函数1：获取歌手id
    # artists_data = get_artist_id(url, base_headers)
    #artists_data.to_csv('artists.csv', index=False)
    # 测试函数2：获取歌手详情页信息
    # artist_infomation, songs_urls = get_artist_detail(urljoin(base_url, artists_data.iloc[0]['href']), base_headers)
    # print(artist_infomation)
    # songs_urls.to_csv('songs_urls.csv', index=False)