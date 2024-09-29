# Website Crawler API

This is a Python-based API built with Flask that crawls a website and retrieves internal pages. For each page, the API provides its URL, metadata, and raw HTML content. The crawling operation supports the optional use of proxies and is limited to a maximum of 50 internal pages.

## Features

- Crawls up to 50 internal pages within the same domain.
- Returns metadata, raw HTML, and URLs for each page.
- Supports optional proxy configuration (IP/Port/User/Pass).
- Simple and lightweight API for web crawling.

## Prerequisites

You need Python 3.x installed on your machine, along with the dependencies listed in the `requirements.txt` file.

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/blademarketing/Crawler.git

Navigate to the project directory:

bash
Copy code
cd Crawler
Install the required dependencies:

bash
Copy code
pip install -r requirements.txt
Run the API server:

bash
Copy code
python main.py
The server will start on http://0.0.0.0:6661 and will be accessible publicly.

API Usage
Endpoint: /crawl
Method: POST
This endpoint accepts a JSON payload containing the URL to crawl and optional proxy settings. It returns a JSON response with up to 50 internal pages, their URLs, metadata, and raw HTML.

Request Body
url (string, required): The URL of the website to crawl.
proxy (object, optional): Proxy settings for crawling, with the following fields:
ip (string): Proxy IP address.
port (string): Proxy port.
user (string): Proxy username.
pass (string): Proxy password.
Example Request (without Proxy)
curl --location --request POST 'http://192.168.0.12:6661/crawl' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url": "https://example.com"
}'

Example Request (with Proxy)
curl --location --request POST 'http://192.168.0.12:6661/crawl' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url": "https://example.com",
    "proxy": {
        "ip": "192.168.0.100",
        "port": "8080",
        "user": "proxyuser",
        "pass": "proxypass"
    }
}'

