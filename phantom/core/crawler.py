import threading
import time
import random
from ..utils.logger import Logger
from ..utils.storage import Storage
from collections import deque
from ..utils.parser import Parser


class Phantom:
    def __init__(
        self,
        urls,
        num_threads=1,
        show_logs=False,
        print_logs=False,
        burnout=700,
        resume=False,
    ):
        print("Phantom Crawler Started")

        self.print_logs = print_logs
        self.thread_count = num_threads
        self.show_logs = show_logs
        self.BURNOUT = burnout
        self.urls = urls

        self.len_urls = len(self.urls)
        self.start_time = time.time()
        self.url = urls[0]
        self.threads = []
        self.id_root = {}

        self.storage = Storage("index", resume=resume)
        self.title_storage = Storage("titles", remote_db=False)
        self.visited_urls = self.storage.fetch_visited()

        self.kill = False
        self.logger = Logger(self.show_logs)
        self.log = self.logger.log

        self.log("INIT-Phantom", "Phantom")

    def crawler(self, id, url):
        burnout = self.BURNOUT
        start_time = time.time()
        local_urls = set(self.visited_urls)
        traversed = []
        queue = deque()
        queue.append(url)
        parser = Parser(self.show_logs)
        epoch = 1

        def status():
            self.log("Status requested", f"Crawler {id}")
            status = f"Crawler {id} \n"
            status += f"Root : {url} \n"
            status += f"Epoch : {epoch} \n"
            # status += f"Traversed : {traversed} \n"
            # status += f"Queue : {queue}"

            self.log(status, f"Crawler {id}")

        while queue and not self.kill:
            if time.time() - start_time > burnout:
                self.log("Burnout", f"Crawler {id}")
                break

            if epoch % 100 == 0:
                status()
                local_urls = self.update_urls(local_urls, id)

            url = queue.popleft()
            # clean the url
            url = parser.clean_url(url)

            if url in local_urls:
                self.log("Already scanned", f"Crawler {id}")
                continue

            local_urls.add(url)
            traversed.append(url)
            self.log(f"Traversing {url}", f"Crawler {id}")
            parsed_data = parser.parse(url)
            neighbors, content, url, title = parsed_data["links"], parsed_data["words"], parsed_data["url"], parsed_data["title"]
            self.storage.add(url, content, title)
            self.title_storage.add(url, title)
            queue.extend(neighbors)
            # self.log(f"Neighbors {neighbors}", f"Crawler {id}")
            epoch += 1

        queue.clear()
        self.log("CRAWLER STOPPED", f"Crawler {id}")

    def update_urls(self, local_url, id):
        """update the local_urls with global index"""
        self.log("Updating URLs", f"Crawler {id}")
        for url in local_url:
            self.visited_urls.add(url)

        return self.visited_urls

    def run(self):
        while len(self.threads) < self.thread_count:
            self.generate(self.urls[random.randint(0, self.len_urls - 1)])

        for thread in self.threads:
            thread.start()

    def generate(self, url):
        id = len(self.threads) + 1
        self.threads.append(threading.Thread(target=self.crawler, args=(id, url)))
        self.id_root[id] = url

    def stop(self):
        self.kill = True
        self.log("STOP-Phantom Issued", "Phantom")

        for threads in self.threads:
            threads.join()

        self.log("STOP-Phantom Stopped", "Phantom")
        self.end()

    def stats(self):
        self.log("Status requested ", "Phantom")
        # stats function
        print("Number of threads : ", self.thread_count)
        print("Threads : ")
        for thread in self.threads:
            print(thread)

        print("thread : Root : ")
        for id, root in self.id_root.items():
            print(f"{id} : {root}")

        print("Time Elapsed : ", time.time() - self.start_time)
        print("Burnout : ", self.BURNOUT)

    def end(self):
        # cleaning function
        self.stats()

        self.storage.save()
        self.title_storage.save()
        self.log("Saved the indices", "Phantom")

        if self.print_logs:
            self.logger.save()

        self.threads.clear()
        self.id_root.clear()
        print("Phantom Crawler Ended")


# phantom = Phantom(num_threads=8,urls=["https://github.com/AnsahMohammad"], show_logs=True, print_logs=True)
# phantom.run()
# time.sleep(30)
# phantom.stop()
