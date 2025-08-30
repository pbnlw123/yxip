from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
import re, sys

URL = "https://stock.hostmonit.com/CloudFlareYesV6"
IPV6_RE = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        # 超时 90 秒 + 只等 DOMContentLoaded（更快）
        page.goto(URL, timeout=90_000, wait_until="domcontentloaded")
        page.wait_for_selector("table tbody tr", timeout=30_000)
        html = page.content()
    except PWTimeout:
        # 超时也不让 job 失败，先留空文件
        html = ""
    browser.close()

ips = IPV6_RE.findall(html)
# 按行打印，方便重定向到 ipv6.txt
for ip in ips:
    print(ip)
