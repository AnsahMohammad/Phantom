import unittest
from unittest.mock import patch, MagicMock
from phantom.utils.logger import Logger
from phantom.utils.parser import Parser
from phantom.utils.storage import Storage
from urllib.parse import urlparse, ParseResult
import time
import json

class TestLogger(unittest.TestCase):
    def test_log(self):
        logger = Logger(show_logs=True, author="John")
        logger.log("Test log", param1="value1", param2="value2")
        expected_log = f"{time.strftime('%H:%M:%S')} : John : Test log | {{'param1': 'value1', 'param2': 'value2'}}"
        self.assertIn(expected_log, logger.logs)

    def test_save(self):
        logger = Logger(show_logs=False, author="Jane")
        logger.log("Test log 1", param1="value1")
        logger.log("Test log 2", param2="value2")
        logger.save("test_logs.txt")
        with open("test_logs.txt", "r") as f:
            saved_logs = f.readlines()
        expected_logs = [
            f"{time.strftime('%H:%M:%S')} : Jane : Test log 1 | {{'param1': 'value1'}}\n",
            f"{time.strftime('%H:%M:%S')} : Jane : Test log 2 | {{'param2': 'value2'}}\n"
        ]
        self.assertEqual(saved_logs, expected_logs)


class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    def test_parser(self):
        site = "www.google.com"
        parsed_site = self.parser.parse(site)
        cleaned_url = self.parser.clean_url(site)
        url_parsed = urlparse(site)

        self.assertEqual(parsed_site["url"], cleaned_url)
        self.assertEqual(parsed_site["title"], "Google")
        self.assertEqual(cleaned_url, "https://www.google.com")

        self.assertIsInstance(parsed_site, dict)
        self.assertIsInstance(cleaned_url, str)
        self.assertIsInstance(url_parsed, ParseResult)

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.storage = Storage(remote_db=False)

    def test_add_and_save_local_db(self):
        # Test the add method
        result = self.storage.add('key', 'value', 'title')
        self.assertTrue(result)
        self.assertEqual(self.storage.data['key'], 'value')

        self.storage.save()
        with open(self.storage.table_name + ".json", 'r') as f:
            data = json.load(f)
        self.assertEqual(data['key'], 'value')

if __name__ == '__main__':
    unittest.main()

if __name__ == "__main__":
    unittest.main()