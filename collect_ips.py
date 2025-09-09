import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表 - 已包含指定网站
urls = [
    'https://api.uouin.com/cloudflare.html', 
    'https://ip.164746.xyz'
]

# 正则表达式用于匹配IP地址（增强版，过滤无效IP）
ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'

# 检查ip.txt文件是否存在，如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个集合用于存储IP地址，自动去重
unique_ips = set()

# 设置请求头，模拟浏览器访问，避免被拦截
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in urls:
    try:
        # 发送HTTP请求获取网页内容，添加超时设置
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根据不同网站的结构找到可能包含IP地址的元素
        if url == 'https://api.uouin.com/cloudflare.html':
            # 针对该网站优化的选择器，查找表格行和可能包含IP的段落
            elements = soup.find_all(['tr', 'p', 'div'])
        elif url == 'https://ip.164746.xyz':
            # 针对该网站的选择器
            elements = soup.find_all('tr')
        else:
            # 默认选择器
            elements = soup.find_all(['li', 'p', 'div'])
        
        # 遍历所有元素，查找IP地址
        for element in elements:
            element_text = element.get_text()
            ip_matches = re.findall(ip_pattern, element_text)
            
            # 如果找到IP地址，添加到集合（自动去重）
            for ip in ip_matches:
                unique_ips.add(ip)
                
        print(f"成功处理: {url}")
        
    except Exception as e:
        print(f"处理{url}时出错: {str(e)}")

# 将收集到的所有唯一IP地址写入文件
with open('ip.txt', 'w') as file:
    for ip in sorted(unique_ips):
        file.write(ip + '\n')

print(f'IP地址已保存到ip.txt文件中，共收集到{len(unique_ips)}个唯一IP。')
    
