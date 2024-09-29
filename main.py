from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import re

app = Flask(__name__)

# Helper function to check if a URL is internal
def is_internal_url(url, base_domain):
    parsed_url = urlparse(url)
    return base_domain == parsed_url.netloc

# Function to crawl the website
def crawl_website(base_url, proxy=None):
    crawled_pages = {}
    visited_urls = set()
    to_crawl = [base_url]
    base_domain = urlparse(base_url).netloc
    count = 0

    proxies = {
        "http": proxy,
        "https": proxy
    } if proxy else None

    headers = {'User-Agent': 'Mozilla/5.0 (compatible; Python Crawler)'}

    while to_crawl and count < 50:
        url = to_crawl.pop(0)
        if url in visited_urls:
            continue

        try:
            # Use proxy if available
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()
            visited_urls.add(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract metadata
            metadata = {meta.get('name', '').lower(): meta.get('content') for meta in soup.find_all('meta')}

            # Store the crawled page data
            crawled_pages[url] = {
                'url': url,
                'metadata': metadata,
                'raw_html': response.text
            }

            # Find all links in the page
            for link in soup.find_all('a', href=True):
                full_url = urljoin(base_url, link['href'])
                if is_internal_url(full_url, base_domain) and full_url not in visited_urls:
                    to_crawl.append(full_url)

            count += 1

        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue

    return crawled_pages

# API endpoint for crawling
@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.json
    base_url = data.get('url')
    proxy_data = data.get('proxy')

    if not base_url:
        return jsonify({"error": "URL is required"}), 400

    # Construct proxy string if provided
    proxy = None
    if proxy_data:
        proxy_user = proxy_data.get('user')
        proxy_pass = proxy_data.get('pass')
        proxy_ip = proxy_data.get('ip')
        proxy_port = proxy_data.get('port')

        if proxy_ip and proxy_port:
            proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}" if proxy_user and proxy_pass else f"http://{proxy_ip}:{proxy_port}"

    # Crawl the website
    crawled_data = crawl_website(base_url, proxy)

    return jsonify(crawled_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6661, debug=True, threaded=True)
