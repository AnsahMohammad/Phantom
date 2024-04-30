import threading
import time

class Phantom:
    def __init__(self, url, num_threads=1):
        print("Phantom Crawler Started")

        self.start_time = time.time()
        self.BURNOUT = 7
        self.url = url
        self.thread_count = num_threads
        self.threads = []
        self.kiLl = False
        self.logs = []
        self.print_logs = False
        self.show_logs = False
        self.id_root = {}

        self.log("INIT-Phantom Issued", "Phantom")

    def crawler(self, id, url):
        while not self.kiLl and time.time() - self.start_time < self.BURNOUT:
            self.log(url, id)
        
        self.log("CRAWLER STOPPED", id)
    
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

    def log(self, content, id=None):
        log_ = f"{time.strftime('%H:%M:%S')} : {id} : {content}"
        
        if self.show_logs:
            print(log_)
        
        if self.print_logs:
            self.logs.append(log_)

    def stats(self):
        # stats function
        print("Number of threads : ", self.thread_count)
        print("Threads : ")
        for thread in self.threads:
            print(thread)
        
        print("thread : Root : ")
        for id, root in self.id_root.items():
            print(f"{id} : {root}")
        
        print("size of logs : ", len(self.logs))
        print("Time Elapsed : ", time.time() - self.start_time)
        print("Burnout : ", self.BURNOUT)
              

    def end(self):
        # cleaning function
        self.stats()

        if self.print_logs:
            with open("logs.txt", "w") as f:
                for log in self.logs:
                    f.write(f"{log}\n")
            self.logs.clear()

            print("Logs saved to logs.txt")
        
        print("Phantom Crawler Ended")

spyder = Phantom("https://www.google.com", 6)
spyder.run()
time.sleep(2)
spyder.stop()

