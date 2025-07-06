'''
这部分代码参考了网络资源：
https://github.com/Tobby-star/music_comment.git
'''
import requests
import json
import base64
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import random
import string
import crawler


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

def get_csrf_token(cookies):
        """从cookie中提取CSRF token"""
        return cookies.get('__csrf', '')

def create_secret_key(size=16):
    """生成随机密钥"""
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(size))

def aes_encrypt(text, sec_key):
    """AES加密"""
    pad_text = pad(text.encode('utf-8'), AES.block_size)
    cipher = AES.new(sec_key.encode('utf-8'), AES.MODE_CBC, b'0102030405060708')
    encrypted = cipher.encrypt(pad_text)
    return base64.b64encode(encrypted).decode('utf-8')

def rsa_encrypt(text, pub_key, modulus):
    """RSA加密"""
    text = text[::-1]  
    rs = pow(int(binascii.hexlify(text.encode('utf-8')), 16), int(pub_key, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)

def encrypt_params(data):
    """加密参数"""
    # 网易云的固定参数
    first_key = '0CoJUm6Qyw8W8jud'
    second_key = '010001'
    third_key = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    
    # 生成随机密钥
    sec_key = create_secret_key()
    
    # 转换数据为JSON字符串
    text = json.dumps(data, separators=(',', ':'))
    
    # 两次AES加密
    enc_text = aes_encrypt(text, first_key)
    params = aes_encrypt(enc_text, sec_key)
    
    # RSA加密密钥
    enc_sec_key = rsa_encrypt(sec_key, second_key, third_key)
    
    return {
        'params': params,
        'encSecKey': enc_sec_key
    }

def get_song_comments(cookies, headers, song_id, offset=0, limit=20):
    """获取歌曲评论"""
    # Cookie和Header配置    
    url = 'https://music.163.com/weapi/comment/resource/comments/get'
    
    # 构建请求数据
    data = {
        'rid': f'R_SO_4_{song_id}',
        'threadId': f'R_SO_4_{song_id}',
        'pageNo': offset // limit + 1,
        'pageSize': limit,
        'cursor': -1,
        'offset': offset,
        'orderType': 1,
        'csrf_token': cookies.get('__csrf', '')
    }
    
    # 加密参数
    encrypted_data = encrypt_params(data)
    
    # 发送请求
    try:
        response = requests.post(
            url,
            data=encrypted_data,
            headers=headers,
            cookies=cookies,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return None

def extract_top_comments(json_data):
    """
    提取前五条热评的信息,并返回评论总数
    
    Args:
        json_data (str): 包含评论信息的JSON数据
    
    Returns:
        tuple: 
            - list: 包含前五条评论信息的列表,每个元素为一个字典,包含评论内容、点赞数和评论时间
            - int: 评论总数
    """
    # data = json.loads(json_data)
    data = json_data
    comments = data["data"]["hotComments"]
    total_count = data["data"]["totalCount"]
    # comments = sorted(comments, key=lambda x: int(x["likedCount"]), reverse=True)
    print(comments[0]["likedCount"])
    if len(comments) >= 5:
        top_comments = comments[:5]
    else:
        top_comments = comments
    
    result = []
    for comment in top_comments:
        comment_info = {
            "content": comment["content"],
            "likedCount": comment["likedCount"],
            "time": comment["timeStr"]
        }
        result.append(comment_info)
    
    return result, total_count

# 使用示例
if __name__ == "__main__":
    song_id = 1472921626
    result = get_song_comments(base_headers, cookies, song_id, offset=0, limit=20)
    top_comments, total_count = extract_top_comments(result)
    # with open(f"{song_id}_top_comments.json", "w", encoding="utf-8") as f:
    #     json.dump(result, f, ensure_ascii=False, indent=2)
    if result:
        print("请求成功!")
        # print(f"返回数据: {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("评论总数:", total_count)
        for comment in top_comments:
            print(f"内容: {comment['content']}, 点赞数: {comment['likedCount']}, 时间: {comment['time']}")
    else:
        print("请求失败")
