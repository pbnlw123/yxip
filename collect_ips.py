import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
import os
from itertools import cycle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Target URLs
urls = [
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://www.wetest.vip/page/cloudflare/address_v6.html',
    'https://api.uouin.com/cloudflare.html',
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://stock.hostmonit.com/CloudFlareYesV6'
]

# Proxy list (replace with your proxies)
proxies = ['http://proxy1:port', 'http://proxy2:port']  # Example proxies
proxy_pool = cycle(proxies) if proxies else None

# Regex for IPv4 and IPv6
ipv4_pattern = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
ipv6_pattern = r'(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}|:(?::[0-9a-fA-F]{1,4}){1,7}|::)'

# Remove existing ip.txt file
try:
    if os.path.exists('ip.txt'):
        os.remove('ip.txt')
except OSError as e:
    print(f"Error deleting ip.txt: {e}")
    exit(1)

# Function to fetch static HTML and extract IPs
def extract_ips_static(url, proxy=None):
    try:
        response = requests.get(url, proxies={'http': proxy, 'https': proxy} if proxy else None, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        elements = soup.find_all(['tr', 'li', 'div'])
        ips = set()
        for element in elements:
            element_text = element.get_text()
            ips.update(re.findall(ipv4_pattern, element_text))
            ips.update(re.findall(ipv6_pattern, element_text))
        return ips
    except requests.RequestException as e:
        print(f"Error fetching {url} (static): {e}")
        return set()

# Async function to fetch AJAX endpoints
async def fetch_ajax(url, session):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content_type = response.headers.get('content-type', '')
                if 'json' in content_type.lower():
                    data = await response.json()
                    return str(data)  # Convert JSON to string for regex
                return await response.text()
    except Exception as e:
        print(f"Error fetching {url} (AJAX): {e}")
    return ''

# Function to extract IPs from AJAX response
def extract_ips_ajax(content):
    ips = set()
    ips.update(re.findall(ipv4_pattern, content))
    ips.update(re.findall(ipv6_pattern, content))
    return ips

# Async function to try fetching IPs via AJAX
async def try_ajax(url, session):
    try:
        # Attempt to fetch common AJAX endpoints (e.g., /api, /data)
        possible_endpoints = [
            url.rstrip('/') + '/api',
            url.replace('.html', '/data'),
            url + '?format=json',
            url  # Try the base URL as well
        ]
        ips = set()
        for endpoint in possible_endpoints:
            content = await fetch_ajax(endpoint, session)
            if content:
                ips.update(extract_ips_ajax(content))
        return ips
    except Exception as e:
        print(f"Error processing AJAX for {url}: {e}")
        return set()

# Function to extract IPs using Selenium (fallback for complex AJAX)
def extract_ips_selenium(url, proxy=None):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        # Wait for dynamic content to load (adjust selector as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tr, li, div'))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        elements = soup.find_all(['tr', 'li', 'div'])
        ips = set()
        for element in elements:
            element_text = element.get_text()
            ips.update(re.findall(ipv4_pattern, element_text))
            ips.update(re.findall(ipv6_pattern, element_text))
        return ips
    except Exception as e:
        print(f"Error fetching {url} (Selenium): {e}")
        return set()

# Main async function to scrape all URLs
async def main():
    all_ips = set()
    async with aiohttp.ClientSession() as session:
        for url in urls:
            print(f"Scraping {url}...")
            proxy = next(proxy_pool) if proxy_pool else None
            
            # Try static HTML first
            static_ips = extract_ips_static(url, proxy)
            all_ips.update(static_ips)
            
            # Try AJAX endpoints
            ajax_ips = await try_ajax(url, session)
            all_ips.update(ajax_ips)
            
            # Fallback to Selenium if no IPs found
            if not static_ips and not ajax_ips:
                print(f"Falling back to Selenium for {url}...")
                selenium_ips = extract_ips_selenium(url, proxy)
                all_ips.update(selenium_ips)
            
            # Respect rate limits
            await asyncio.sleep(1)

    # Write unique IPs to file
    try:
        with open('ip.txt', 'w') as file:
            for ip in sorted(all_ips):
                file.write(ip + '\n')
        print(f'{len(all_ips)} unique IP addresses saved to ip.txt.')
    except OSError as e:
        print(f"Error writing to ip.txt: {e}")

# Run the async main function
if __name__ == '__main__':
    asyncio.run(main())
