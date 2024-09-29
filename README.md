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
