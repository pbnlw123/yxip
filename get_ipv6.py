from playwright.sync_api import sync_playwright
import re

URL = "https://stock.hostmonit.com/CloudFlareYesV6"
IPV6_RE = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle")
    page.wait_for_selector("table tbody tr")
    html = page.content()
    browser.close()

ips = IPV6_RE.findall(html)
for ip in ips:
    print(ip)
