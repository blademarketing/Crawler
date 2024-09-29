import os
import sys
import asyncio
import aiohttp
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv
from time import sleep

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Load configuration from environment variables
MAX_PAGES = int(os.getenv("MAX_PAGES", 50))
MAX_DEPTH = int(os.getenv("MAX_DEPTH", 2))
MAX_CONCURRENT_TASKS = int(os.getenv("MAX_CONCURRENT_TASKS", 100))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))

# Shared stats
stats = {
    "running_tasks": 0,
    "completed_tasks": 0,
    "error_tasks": 0,
    "total_urls": 0
}

# Helper function to check if a URL is internal
def is_internal_url(url, base_domain):
    parsed_url = urlparse(url)
    return base_domain == parsed_url.netloc

# Async function to fetch a URL
async def fetch(session, url):
    try:
        async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
            return await response.text()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        stats['error_tasks'] += 1
        return None

# Async function to crawl a single page
async def crawl_page(session, url, depth, base_url, base_domain, visited_urls):
    if depth > MAX_DEPTH or len(visited_urls) >= MAX_PAGES:
        return None

    html_content = await fetch(session, url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract metadata
    metadata = {meta.get('name', '').lower(): meta.get('content') for meta in soup.find_all('meta')}
    visited_urls.add(url)

    crawled_page = {
        'url': url,
        'metadata': metadata,
        'raw_html': html_content
    }

    # Find internal links
    links = []
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        if is_internal_url(full_url, base_domain):
            links.append(full_url)

    return crawled_page, links

# Async function to handle the crawling process
async def crawl_website(base_url, proxy=None):
    base_domain = urlparse(base_url).netloc
    visited_urls = set()
    all_crawled_data = {}

    async with aiohttp.ClientSession() as session:
        to_crawl = [(base_url, 1)]  # Starting with the base URL and depth = 1

        while to_crawl and len(visited_urls) < MAX_PAGES:
            tasks = []
            for url, depth in to_crawl:
                stats['running_tasks'] += 1
                tasks.append(crawl_page(session, url, depth, base_url, base_domain, visited_urls))

            results = await asyncio.gather(*tasks)
            to_crawl = []

            # Process results and prepare for the next depth
            for result in results:
                if result:
                    crawled_page, links = result
                    all_crawled_data[crawled_page['url']] = crawled_page

                    next_depth = depth + 1
                    if next_depth <= MAX_DEPTH:
                        to_crawl.extend([(link, next_depth) for link in links if len(visited_urls) < MAX_PAGES])

            stats['completed_tasks'] += len(results)

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

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    crawled_data = loop.run_until_complete(crawl_website(base_url, proxy))

    return jsonify(crawled_data), 200  # Return the crawled data in the original format

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6661, debug=True, threaded=True)
