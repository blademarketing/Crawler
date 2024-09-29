import os
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get max pages and depth from environment variables
MAX_PAGES = int(os.getenv("MAX_PAGES", 50))
MAX_DEPTH = int(os.getenv("MAX_DEPTH", 1))

# Helper function to check if a URL is internal
def is_internal_url(url, base_domain):
    parsed_url = urlparse(url)
    return base_domain == parsed_url.netloc

# Function to crawl a single page
def crawl_page(url, base_url, base_domain, depth, visited_urls, proxies):
    if depth > MAX_DEPTH:
        return None

    if url in visited_urls or len(visited_urls) >= MAX_PAGES:
        return None

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; Python Crawler)'}
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract metadata
        metadata = {meta.get('name', '').lower(): meta.get('content') for meta in soup.find_all('meta')}

        visited_urls.add(url)

        crawled_page = {
            'url': url,
            'metadata': metadata,
            'raw_html': response.text
        }

        # Find internal links and crawl them (limited by depth and max pages)
        links = []
        for link in soup.find_all('a', href=True):
            full_url = urljoin(base_url, link['href'])
            if is_internal_url(full_url, base_domain):
                links.append(full_url)

        return crawled_page, links

    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

# Function to crawl the website with threading
def crawl_website(base_url, proxy=None):
    visited_urls = set()
    base_domain = urlparse(base_url).netloc
    to_crawl = [(base_url, 1)]  # Starting depth is 1
    
    proxies = {"http": proxy, "https": proxy} if proxy else None

    all_crawled_data = {}

    with ThreadPoolExecutor() as executor:
        while to_crawl and len(visited_urls) < MAX_PAGES:
            # Get the next set of pages to crawl (at the same depth)
            current_depth_crawl = [executor.submit(crawl_page, url, base_url, base_domain, depth, visited_urls, proxies) for url, depth in to_crawl]
            to_crawl = []

            # Process the crawled pages
            for future in current_depth_crawl:
                result = future.result()
                if result:
                    crawled_page, links = result
                    all_crawled_data[crawled_page['url']] = crawled_page

                    # Queue the links for the next depth level
                    next_depth = depth + 1  # Move to the next depth level
                    if next_depth <= MAX_DEPTH:
                        to_crawl.extend([(link, next_depth) for link in links if link not in visited_urls and len(visited_urls) < MAX_PAGES])

    return all_crawled_data

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
