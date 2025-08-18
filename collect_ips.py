import requests
from bs4 import BeautifulSoup
import re
import os

# Target URLs
urls = [
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://www.wetest.vip/page/cloudflare/address_v6.html',
    'https://api.uouin.com/cloudflare.html',
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://stock.hostmonit.com/CloudFlareYesV6'
]

# Regex for IPv4 (0-255 per octet)
ipv4_pattern = r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'

# Regex for IPv6 (full and abbreviated forms)
ipv6_pattern = r'(?:(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}|:(?::[0-9a-fA-F]{1,4}){1,7}|::)'

# Remove existing ip.txt file
try:
    if os.path.exists('ip.txt'):
        os.remove('ip.txt')
except OSError as e:
    print(f"Error deleting ip.txt: {e}")
    exit(1)

# Function to fetch and parse IPs from a URL
def extract_ips(url):
    try:
        # Send HTTP request
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple elements to find IPs (<tr>, <li>, <div>)
        elements = soup.find_all(['tr', 'li', 'div'])
        
        # Extract IPs
        ips = []
        for element in elements:
            element_text = element.get_text()
            # Find IPv4 addresses
            ipv4_matches = re.findall(ipv4_pattern, element_text)
            # Find IPv6 addresses
            ipv6_matches = re.findall(ipv6_pattern, element_text)
            # Combine and label IPs
            for ip in ipv4_matches:
                ips.append(f"IPv4: {ip}")
            for ip in ipv6_matches:
                ips.append(f"IPv6: {ip}")
        
        return ips
    
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

# Collect IPs from all URLs and write to file
try:
    with open('ip.txt', 'w') as file:
        for url in urls:
            print(f"Scraping {url}...")
            ips = extract_ips(url)
            for ip in ips:
                file.write(ip + '\n')
    print('IP addresses saved to ip.txt.')
except OSError as e:
    print(f"Error writing to ip.txt: {e}")
