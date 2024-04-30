import threading
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
from logger import Logger

class Phantom:
    def __init__(self, url, num_threads=1, show_logs=False, print_logs=False, burnout=700):
        print("Phantom Crawler Started")

        self.start_time = time.time()
        self.print_logs = print_logs
        self.thread_count = num_threads
        self.show_logs = show_logs
        self.BURNOUT = burnout
        
        self.url = url
        self.threads = []
        self.id_root = {}
        self.urls = set()
        self.kill = False
        self.logger = Logger(self.show_logs)
        self.log = self.logger.log
        self.storage = Storage()

        self.log("INIT-Phantom", "Phantom")

    def crawler(self, id, url):
        burnout = self.BURNOUT
        start_time = time.time()
        local_urls = set()
        traversed = []
        queue = []
        queue.append(url)
        parser = Parser(self.show_logs)
        epoch = 1

        def status():
            self.log("Status requested", f"Crawler {id}")
            status = f"Crawler {id} \n"
            status += f"Root : {url} \n"
            status += f"Epoch : {epoch} \n"
            # status += f"Traversed : {traversed} \n"
            status += f"Queue : {queue}"

            self.log(status, f"Crawler {id}")

        while queue and not self.kill:
            if time.time() - start_time > burnout:
                self.log("Burnout", f"Crawler {id}")
                break

            if epoch % 100 == 0:
                status()
                local_urls = self.update_urls(local_urls, id)

            url = queue.pop(0)

            if url in local_urls:
                self.log("Already scanned", f"Crawler {id}")
                continue
            
            local_urls.add(url)
            traversed.append(url)
            self.log(f"Traversing {url}", f"Crawler {id}")
            neighbors, content = parser.parse(url)
            self.storage.add(url, content)
            queue.extend(neighbors)
            # self.log(f"Neighbors {neighbors}", f"Crawler {id}")
            epoch += 1
        
        queue.clear()
        self.log("CRAWLER STOPPED", f"Crawler {id}")

    # def crawler(self, id, url):
    #     """Crawler using Crawler Object"""
    #     crawler = Crawler(url, id)
    #     while not self.kill:
    #         crawler.crawl()
    #         # crawler.skip()

    #     crawler.kill()
            
    def update_urls(self, local_url, id):
        """update the local_urls with global index"""
        self.log("Updating URLs", f"Crawler {id}")
        for url in local_url:
            self.urls.add(url)

        return self.urls

    def run(self):
        while len(self.threads) < self.thread_count:
            self.generate(self.url)

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
        self.log("Saved the indices", "Phantom")

        if self.print_logs:
            self.logger.save()
        
        self.threads.clear()
        self.id_root.clear()
        print("Phantom Crawler Ended")

class Parser:
    def __init__(self, show_logs):
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

        cleaned_url = self.clean_url(url)
        content = self.fetch(cleaned_url)

        soup = BeautifulSoup(content, 'html.parser')

        text = soup.get_text()
        words = text.split()
        links = [urljoin(url, link.get('href')) for link in soup.find_all('a')]

        return links, words

class Crawler:
    def __init__(self, url, id):
        self.id = id
        self.url = url
        self.running = True
        self.kill = False
        self.show_logs = True
        self.traversed = set()
        self.log = Logger(self.show_logs).log
        self.parse = Parser().parse

    def status(self):
        self.log("Status requested", f"Crawler {self.id}")
        status = f"Crawler {self.id} \n"
        status += "Status : {self.running} \n"
        status += f"Root : {self.url} \n"
        status += f"Traversed : {self.traversed} \n"

        print(status)
        self.log(status, f"Crawler {self.id}")

    def crawl(self):
        self.log("Crawling started", f"Crawler {self.id}")
        queue = []
        queue.append(self.url)

        while queue and self.running and not self.kill:
            url = queue.pop(0)
            
            if url in self.traversed:
                self.log(f"Already traversed {url}", f"Crawler {self.id}")
                continue


            self.log(f"Traverse {self.url}", f"Crawler {self.id}")
            self.traversed.add(self.url)
            
            neighbours = self.parse(self.url)
            queue.extend(neighbours)
        
        self.running = False
        self.log("Crawling stopped", f"Crawler {self.id}")
    
    def kill(self):
        self.log("Kill issued", f"Crawler {self.id}")
        self.kill = True
        self.status()

        self.traversed.clear()
        self.log("Crawler killed", f"Crawler {self.id}")

    def skip(self):
        pass

    def pause(self):
        self.log("Pause issued", f"Crawler {self.id}")
        self.running = False
    
    def resume(self):
        self.log("Resume issued", f"Crawler {self.id}")
        self.running = True

class Storage:
    def __init__(self, filename="index.json"):
        self.filename = filename
        self.data = {}

    def add(self, key, value):
        self.data[key] = value

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

# phantom = Phantom("https://github.com/AnsahMohammad", 6, show_logs=True, print_logs=True)
# phantom.run()
# time.sleep(30)
# phantom.stop()
