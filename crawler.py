import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re
from fake_useragent import UserAgent
import json
from urllib.parse import urljoin
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        cookies = {}
        for cookie in cookie_str.split(";"):
            if "=" in cookie:
                key, value = cookie.split("=", 1)
                cookies[key.strip()] = value.strip()
            else:
                logger.warning(f"Invalid cookie format: {cookie}")
        return cookies
    except Exception as e:
        logger.error(f"Error parsing cookies: {e}")
        return {}


# 获取歌手id
def get_artist_id(url, headers=None, cookies=None):
    """
    爬取对应页面下的歌手id，歌手名称等基本信息
    """
    try:
        if headers is None:
            headers = {"User-Agent": UserAgent().random}    
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()   
        soup = BeautifulSoup(response.text, "html.parser")
        # 获取包含歌手信息的标签
        artists = soup.find_all("a", class_="nm nm-icn f-thide s-fc0")    
        if not artists:
            logger.warning("No artists found on the page")
            return pd.DataFrame(columns=["name", "id"])
        artists_data = []
        # 将歌手名称和id进行存储
        for a in artists:
            try:
                artist_url = a.get("href", None)
                if not artist_url:
                    logger.warning(f"Artist URL not found, skipping")
                    continue         
                id_match = re.search(r"id=(\d+)", artist_url)
                if not id_match:
                    logger.warning(f"Artist ID not found in URL: {artist_url}")
                    continue          
                artist_id = id_match.group(1)
                artist_name = a.get_text(strip=True)   
                if not artist_name:
                    logger.warning(f"Artist name not found in URL: {artist_url}")
                    continue
                row = {
                    "name": artist_name,
                    "id": artist_id,
                }
                artists_data.append(row)       
            except Exception as e:
                logger.error(f"Error processing artist element: {e}")
                continue       
        artists_data = pd.DataFrame(artists_data)
        logger.info(f"Successfully extracted {len(artists_data)} artists")
        return artists_data   
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return pd.DataFrame(columns=["name", "id"])
    except Exception as e:
        logger.error(f"Unexpected error in get_artist_id: {e}")
        return pd.DataFrame(columns=["name", "id"])


# 获取歌手详情页信息
def get_artist_detail(id, headers=None, cookies=None):
    """
    爬取歌手详情页信息, 获取歌手简介，歌手图片，歌曲id等；
    其中：歌手基本信息，包含姓名，简介，图片url，等返回一个字典；
    其下默认展示在首页的歌曲（100首）的url返回一个表格
    """
    try:
        url = urljoin(base_url, f"artist?id={id}")
        if headers is None:
            headers = {"User-Agent": UserAgent().random}   
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()      
        soup = BeautifulSoup(response.text, "html.parser")     
        # 获取并整合歌手基本信息
        artist_infomation = {
            "name": None,
            "image_url": None,
            "abstract": None,
            "url": url,
        }        
        # 获取歌手姓名
        try:
            name_element = soup.find("h2", id="artist-name")
            if name_element:
                artist_infomation["name"] = name_element.get_text(strip=True)
            else:
                logger.warning(F"Artist name not found at URL: {url}")
        except Exception as e:
            logger.error(f"Error getting artist name: {e}")  
        # 获取歌手图片
        try:
            image_meta = soup.find("meta", property="og:image")
            if image_meta:
                artist_infomation["image_url"] = image_meta.get("content")
            else:
                logger.warning(F"Artist image URL not found at URL: {url}")
        except Exception as e:
            logger.error(f"Error getting artist image: {e}")    
        # 获取歌手简介
        try:
            abstract_meta = soup.find("meta", property="og:abstract")
            if abstract_meta:
                artist_infomation["abstract"] = abstract_meta.get("content")
            else:
                logger.warning("Artist abstract not found")
        except Exception as e:
            logger.error(f"Error getting artist abstract: {e}")     
        # 获取歌曲id
        songs_urls = []
        try:
            songs = soup.find_all("a", href=re.compile(r"/song\?id=\d+$"))    
            for song in songs:
                try:
                    song_href = song.get("href")
                    if not song_href:
                        logger.warning(f"Song URL not found, skipping")
                        continue            
                    song_url = urljoin(base_url, song_href)
                    id_match = re.search(r"id=(\d+)", song_url)
                    if not id_match:
                        logger.warning(f"Song ID not found in URL: {song_url}")
                        continue            
                    song_id = id_match.group(1)
                    song_name = song.get_text(strip=True)                    
                    if song_name:
                        row = {
                            "artist": artist_infomation["name"] or "Unknown",
                            "name": song_name,
                            "id": song_id,
                        }
                        songs_urls.append(row)                       
                except Exception as e:
                    logger.error(f"Error processing song element: {e}")
                    continue
            logger.info(f"Successfully extracted {len(songs_urls)} songs")     
        except Exception as e:
            logger.error(f"Error getting songs: {e}") 
        songs_urls = pd.DataFrame(songs_urls)
        return artist_infomation, songs_urls    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {
            "name": None,
            "image_url": None,
            "abstract": None,
            "url": None,
        }, pd.DataFrame(columns=["artist", "name", "id"])
    except Exception as e:
        logger.error(f"Unexpected error in get_artist_detail: {e}")
        return {
            "name": None,
            "image_url": None,
            "abstract": None,
            "url": None,
        }, pd.DataFrame(columns=["artist", "name", "id"])


def get_songs_detail(id, headers=None, cookies=None):
    """
    爬取歌曲详情页信息，获取歌曲名称，歌手名称，专辑名称，歌曲简介，歌曲url，歌曲图片url，歌曲时长，歌词等
    """
    try:
        # 爬取歌曲详情页
        url = urljoin(base_url, f"song?id={id}")
        if headers is None:
            headers = {"User-Agent": UserAgent().random}
        response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
        response.raise_for_status()     
        soup = BeautifulSoup(response.text, "html.parser")      
        # 初始化结果字典
        result = {
            'title': None,
            'artist': None,
            'album': None,
            'description': None,
            'image_url': None,
            'lyric': None,
            'time_points': [],
            'url': url,
            'lyric_url': None,
        }    
        # 获取歌曲基本信息
        try:
            title_meta = soup.find('meta', property="og:title")
            if title_meta:
                result['title'] = title_meta.get('content')
            else:
                logger.warning(f"Song title not found at URL: {url}")
        except Exception as e:
            logger.error(f"Error getting song title: {e}")
        try:
            artist_meta = soup.find('meta', property="og:music:artist")
            if artist_meta:
                result['artist'] = artist_meta.get('content')
            else:
                logger.warning(f"Song artist not found at URL: {url}")
        except Exception as e:
            logger.error(f"Error getting song artist: {e}")
        try:
            album_meta = soup.find('meta', property="og:music:album")
            if album_meta:
                result['album'] = album_meta.get('content')
            else:
                logger.warning(f"Song album not found at URL: {url}")
        except Exception as e:
            logger.error(f"Error getting song album: {e}")
        
        try:
            description_meta = soup.find('meta', property="og:description")
            if description_meta:
                result['description'] = description_meta.get('content')
            else:
                logger.warning(f"Song description not found at URL: {url}")
        except Exception as e:
            logger.error(f"Error getting song description: {e}")
        
        try:
            image_meta = soup.find('meta', property="og:image")
            if image_meta:
                result['image_url'] = image_meta.get('content')
            else:
                logger.warning(f"Song image URL not found at URL: {url}")
        except Exception as e:
            logger.error(f"Error getting song image: {e}")
        
        # 获取歌词（去除时间轴）
        try:
            lyric_url = urljoin(base_url, f"api/song/media?id={id}")
            result['lyric_url'] = lyric_url  
            lyric_response = requests.get(lyric_url, headers=headers, cookies=cookies, timeout=10)
            lyric_response.raise_for_status()    
            lyric_data = lyric_response.json()
            if 'lyric' in lyric_data and lyric_data['lyric']:
                raw_lyric = lyric_data['lyric']
                lines = raw_lyric.strip().split('\n')
                time_points = [] 
                cleaned_lyrics = []      
                for line in lines:
                    try:
                        match = re.match(r'^\[(\d{2}:\d{2}\.\d+)\](.*)', line)
                        if match:
                            time_point = match.group(1)  
                            lyric_text = match.group(2).strip()                         
                            time_points.append(time_point)
                            cleaned_lyrics.append(lyric_text)
                    except Exception as e:
                        logger.error(f"Error processing lyric line: {line}, error: {e}")
                        continue
                result['lyric'] = '\n'.join(cleaned_lyrics)
                result['time_points'] = time_points        
            else:
                logger.warning("Lyric data not found in response")         
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get lyrics: {e}")
        except (KeyError, TypeError, json.JSONDecodeError) as e:
            logger.error(f"Error parsing lyric response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting lyrics: {e}")
        logger.info(f"Successfully extracted song details for ID: {id}")
        return result    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {
            'title': None,
            'artist': None,
            'album': None,
            'description': None,
            'image_url': None,
            'lyric': None,
            'time_points': [],
            'url': None,
            'lyric_url': None,
        }
    except Exception as e:
        logger.error(f"Unexpected error in get_songs_detail: {e}")
        return {
            'title': None,
            'artist': None,
            'album': None,
            'description': None,
            'image_url': None,
            'lyric': None,
            'time_points': [],
            'url': None,
            'lyric_url': None,
        }


if __name__ == "__main__":
    print(0)