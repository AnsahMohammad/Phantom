from bs4 import BeautifulSoup
from .logger import Logger
from urllib.parse import urlparse, urljoin, urlunparse
import json
import requests


class Parser:
    def __init__(self, show_logs=True):
        self.show_logs = show_logs
        self.log = Logger(self.show_logs, "phantom-parser").log


    def clean_url(self, url):
        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'https://' + url
            parsed = urlparse(url)
        cleaned = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
        return cleaned

    def fetch(self, url):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.content
        except Exception as e:
            self.log(f"Failed to fetch {url}: {e}", "Parser")
            return None

    def parse(self, url) -> dict:
        self.log(f"parsing {url}", "Parser")

        url = self.clean_url(url)
        content = self.fetch(url)

        if content is None:
            return {"links": [], "words": [], "url": url, "title": None}

        try:
            soup = BeautifulSoup(content, "html.parser")
        except Exception as e:
            self.log(f"Failed to parse {url}: {e}", "Parser")
            return {"links": [], "words": [], "url": url, "title": None}
            

        title = soup.title.string if soup.title else None

        text = soup.get_text()
        words = text.split()
        links = [self.clean_url(urljoin(url, link.get("href"))) for link in soup.find_all("a")]

        return {"links": links, "words": words, "url": url, "title": title}

    def url_parser(self, url) -> dict:
        self.log(f"url parsing {url}", "Parser")

        cleaned_url = self.clean_url(url)
        content = self.fetch(cleaned_url)

        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string
        return {"title": title, "url": cleaned_url}


if __name__ == "__main__":
    parser = Parser()
    sites = ["www.google.com", "https://www.google.com", "google.com/", "m.google.com", "https://www.google.co.in/intl/en/about/products?tab=wh"]
    for site in sites:
        print(parser.parse(site))
        print(parser.url_parser(site))
        print(parser.clean_url(site))
        print(urlparse(site))
        print("-"*50)
