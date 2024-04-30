import threading
import time
import random

class Phantom:
    def __init__(self, url, num_threads=1):
        print("Phantom Crawler Started")

        self.start_time = time.time()
        self.BURNOUT = 7
        self.url = url
        self.thread_count = num_threads
        self.threads = []
        self.kiLl = False
        self.print_logs = False
        self.show_logs = True
        self.id_root = {}
        self.urls = set()
        self.log = Logger(self.show_logs).log

        self.log("INIT-Phantom Issued", "Phantom")

    def crawler(self, id, url):
        kill = self.kiLl
        burnout = self.BURNOUT
        log = self.log
        local_urls = set()
        queue = []
        queue.append(url)

        # while not kill and time.time() - self.start_time < burnout:
        while queue and not kill:
            url = queue.pop(0)
            log(url, id)

            if url in local_urls or self.scanned(url):
                log("Already scanned", id)
                continue
            
            local_urls.add(url)
            self.urls.add(url)

            parser = Parser(url)
            neighbors = parser.parse()
            queue.extend(neighbors)
        
        queue.clear()
        log("CRAWLER STOPPED", id)
    
    def scanned(self, url):
        if url in self.urls:
            return True

        return False

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
        self.kiLl = True
        self.log("STOP-Phantom Issued", "Phantom")
        
        for threads in self.threads:
            threads.join()
        
        self.log("STOP-Phantom Stopped", "Phantom")
        self.end()

    def stats(self):
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

        if self.print_logs:
            self.log.save()
        
        self.threads.clear()
        self.id_root.clear()
        print("Phantom Crawler Ended")

class Crawler:
    def __init__(self, url):
        self.url = url
        self.show_logs = True

    def crawl(self):
        if self.show_logs:
            spyder.log("crawling : ",self.url)

        return [f"hello{random.randint(0,1000)}.com"]

class Parser:
    def __init__(self, url):
        self.url = url
        self.show_logs = True
        self.log = Logger(self.show_logs).log

    def parse(self):
        if self.show_logs:
            self.log(f"parsing {self.url}", "Parser")

        return [f"hello{random.randint(0,1000)}.com"]

class Logger:
    def __init__(self, show_logs=True):
        self.show_logs = show_logs
        self.logs = []

    def log(self, content, id=None, **kwargs):
        log_ = f"{time.strftime('%H:%M:%S')} : "
        if id:
            log_ += f"{id} : "
        
        log_ += f"{content} | {kwargs}"

        self.logs.append(log_)
        if self.show_logs:
            print(log_)
    
    def save(self):
        with open("logs.txt", "w") as f:
            for log in self.logs:
                f.write(log + "\n")
        self.log("Logs saved to logs.txt", "Log")
        self.logs.clear()


spyder = Phantom("https://www.google.com", 6)
spyder.run()
time.sleep(5)
spyder.stop()

