import requests
from bs4 import BeautifulSoup
import re
import os

# 目标 URL
urls = [
    "https://api.uouin.com/cloudflare.html",
    "https://ip.164746.xyz"
]

# ✅ 一个正则同时匹配合法 IPv4 和 IPv6（压缩/完整写法都支持）
ip_pattern = re.compile(r'''
    \b
    (?:
        (?: (?:25[0-5]|2[0-4]\d|[01]?\d{1,2}) \.){3}
        (?:25[0-5]|2[0-4]\d|[01]?\d{1,2})                # IPv4
      |
        (?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}          # IPv6 完整写法
      | (?:[0-9a-fA-F]{1,4}:)*::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}  # IPv6 压缩写法
      | ::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}
      | (?:[0-9a-fA-F]{1,4}:){1,7}:
    )
    \b
''', re.VERBOSE)

# 删除旧文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

seen = set()          # 去重用
with open('ip.txt', 'w', encoding='utf-8') as f:
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')

            for tr in soup.find_all('tr'):
                for ip in ip_pattern.findall(tr.get_text()):
                    # 简单合法性二次校验（可选）
                    if ip not in seen:
                        seen.add(ip)
                        f.write(ip + '\n')
        except Exception as e:
            print(f"[ERROR] {url} -> {e}")

print('IPv4 & IPv6 已写入 ip.txt')
