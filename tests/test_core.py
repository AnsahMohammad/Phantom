import unittest
import threading
import os
from phantom.core.crawler import Phantom
import time

class TestPhantom(unittest.TestCase):
    def setUp(self):
        self.num_thread = 6
        self.phantom = Phantom(urls=["https://www.google.com"], num_threads=self.num_thread, show_logs=False, print_logs=False)

    def test_phantom_run_and_stop(self):
        # Start the phantom in a separate thread
        self.phantom.run()

        # Stop the phantom
        self.phantom.stop()

        # Assert the thread count
        self.assertEqual(self.phantom.thread_count, self.num_thread)

        # Check if the files were created
        self.assertTrue(os.path.isfile('index.json'))
        self.assertTrue(os.path.isfile('titles.json'))

if __name__ == '__main__':
    unittest.main()