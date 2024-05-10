"""
IGNORE TEST CASE AS WIP
"""

# import unittest
# import threading
# import time
# from phantom.distrib.master_node import Server
# from phantom.distrib.worker_node import Crawler

# # class TestServer(unittest.TestCase):
# #     def setUp(self):
# #         self.server = Server(port=9999)

# #     def test_server_run_and_stop(self):
# #         # Start the server in a separate thread
# #         server_thread = threading.Thread(target=self.server.start)
# #         server_thread.start()

# #         time.sleep(5)

# #         # Stop the server
# #         self.server.stop()

# #         # Check if the server stopped successfully
# #         self.assertFalse(self.server.running)


# # class TestCrawler(unittest.TestCase):
# #     def setUp(self):
# #         self.crawler = Crawler(server_port=9999)

# #     def test_crawler_run_and_stop(self):
# #         # Start the crawler in a separate thread
# #         crawler_thread = threading.Thread(target=self.crawler.connect)
# #         crawler_thread.start()

# #         time.sleep(5)

# #         # Stop the crawler
# #         self.crawler.stop()

# #         # Check if the crawler stopped successfully
# #         self.assertFalse(self.crawler.running)

# # class TestDistrib(unittest.TestCase):
# #     @unittest.skip("Skipping this as work in progress(WIP)")
# #     def setUp(self):
# #         self.server = Server(port=9997)
# #         self.crawler = Crawler(server_port=9997)

# #     @unittest.skip("Skipping this as work in progress(WIP)")
# #     def test_server_run_and_stop(self):
# #         # Start the server in a separate thread
# #         server_thread = threading.Thread(target=self.server.start)
# #         server_thread.start()

# #         print("Hello")

# #         crawler_thread = threading.Thread(target=self.crawler.connect)
# #         crawler_thread.start()

# #         self.crawler.stop()
# #         crawler_thread.join()
# #         self.assertFalse(self.crawler.running)

# #         self.server.stop()
# #         server_thread.join()
# #         self.assertFalse(self.server.running)

# if __name__ == '__main__':
#     unittest.main()
