from bs4 import BeautifulSoup
from .logger import Logger
from urllib.parse import urlparse, urljoin
import json
import requests


class Parser:
    def __init__(self, show_logs=True):
        self.show_logs = show_logs
        self.log = Logger(self.show_logs).log

    def clean_url(self, url):
        parsed = urlparse(url)
        cleaned = parsed.scheme + "://" + parsed.netloc + parsed.path
        return cleaned

    def fetch(self, url):
        response = requests.get(url)
        return response.content

    def parse(self, url):
        self.log(f"parsing {url}", "Parser")

        # cleaned_url = self.clean_url(url)   since already cleaned disabled
        content = self.fetch(url)

        soup = BeautifulSoup(content, "html.parser")

        title = soup.title.string if soup.title else None

        text = soup.get_text()
        words = text.split()
        links = [urljoin(url, link.get("href")) for link in soup.find_all("a")]

        return links, words, url, title

    def url_parser(self, url):
        self.log(f"parsing {url}", "Parser")

        cleaned_url = self.clean_url(url)
        content = self.fetch(cleaned_url)

        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string
        return (title, cleaned_url)
