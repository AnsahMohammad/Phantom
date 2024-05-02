import socket
import threading
from .logger import Logger
from .phantom_engine import Parser
import time
import json

class Crawler:
    def __init__(self, server_host="0.0.0.0", server_port=9999):
        self.server_host = server_host
        self.server_port = server_port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = None
        self.threads = []
        self.id = -1
        self.running = False
        self.kill = False
        self.crawling = False
        self.setup_ = False

        print(f"Crawler init to {self.server_host}:{self.server_port}")

    def connect(self):
        self.running = True
        # connection to server
        self.client.connect((self.server_host, self.server_port))

        l_address = self.client.getsockname()
        self.id = l_address[1]

        self.initialize()
        
        self.log("connected to server", "<connect>")
        self.log("id assigned", f"Crawler {self.id}")


        self.thread = threading.Thread(target=self.listen_to_server)
        self.thread.start()
        self.threads.append(self.thread) # adding to the thread list
        self.log("thread started", "<connect>")

        while not self.kill:
            command = input("Enter command: ")
            if command == "stop":
                self.kill = True
                break
            elif command == "send":
                message = input("Enter message: ")
                self.send(message)
            elif command == "status":
                self.status()
            elif command == "run":
                self.running = not self.running
                self.status()
            elif command == "save":
                self.store()
                self.log("stored the data")
            else:
                print("Invalid command")

        self.log("closing connection", "<connect>")        
        self.stop()

    def listen_to_server(self):
        self.log("Listening to server")
        self.client.settimeout(1)
        while not self.kill:
            try:
                response = self.client.recv(1024)
                response = response.decode()
                self.log(f"Received: {response}")

                action = response.split(",")[0]

                if action == "setup":
                    self.setup(response)
                elif action == "status":
                    self.status()
                elif action == "append":
                    self.add_queue(response)
                elif action == "restart":
                    self.crawling = False
                    self.initialize()
                elif action == "crawl":
                    if not self.setup_:
                        self.log("Setup not done", f"Crawler {self.id}")
                        continue
                    if self.crawling:
                        self.log("Crawl already running", f"Crawler {self.id}")
                        continue
                    self.log("Starting the crawl")
                    self.crawl_t = threading.Thread(target=self.crawl)
                    self.crawl_t.start()
                    self.threads.append(self.crawl_t)
                elif action == "stop":
                    self.log("close requested from server")
                    self.kill = True
                    break
            except socket.timeout:
                continue
        
        self.running = False
        self.log("waiting to be closed")
    
    def setup(self, response):
        # recieved in format setup,url,burnout
        data = response.split(",")
        self.url = str(data[1])
        if len(data) < 3:
            self.burnout = 600
        else:
            self.burnout = int(data[2])
        self.setup_ = True

        self.log("Setup done", f"Crawler {self.id}")
        self.status()

    def add_queue(self, response):
        # add url to the queue
        data = response.split(",")
        if len(data) > 1:
            self.queue.extend(data[1:])

        self.log(f"queue extended by {len(data)-1}", f"Crawler {self.id}")
        self.status()

    def initialize(self):
        self.local_urls = set()
        self.traversed = []
        self.queue = []
        self.start_time = time.time()
        self.parser = Parser(show_logs=True)
        self.log = Logger(show_logs=True, author=f"crawler-{self.id}").log
        self.url = "None"

        self.index_storage = Storage(f"index-{self.id}.json")
        self.title_storage = Storage(f"title-{self.id}.json")

    def crawl(self):
        self.log("Crawling started", f"Crawl {self.id}")
        self.status()
        self.start_time = time.time()
        self.crawling = True
        self.queue.append(self.url)
        epoch = 1
        while self.queue and self.running:
            if time.time() - self.start_time > self.burnout:
                self.log("Burnout", f"Crawl {id}")
                break

            if epoch % 50 == 0:
                self.status()
                self.store()

            try:
                url = self.queue.pop(0)
                url = self.parser.clean_url(url)

                if url in self.local_urls:
                    self.log("Already scanned", f"Crawl {id}")
                    continue

                self.local_urls.add(url)
                self.traversed.append(url)
                self.log(f"Traversing {url}", f"Crawl {id}")
                neighbors, content, url, title = self.parser.parse(url)
                self.index_storage.add(url, content)
                self.title_storage.add(url, title)
                self.queue.extend(neighbors)
                epoch += 1
            except:
                continue

        self.running = False
        self.crawling = False
        self.log("Crawling stopped", f"Crawler {self.id}")

    def store(self):
        self.index_storage.save()
        self.title_storage.save()
        self.log("Data stored", f"Crawler {self.id}")
        self.send("store,0".encode())

    def stop(self):
        self.log("Kill issued", f"Crawler {self.id}")
        self.kill = True
        self.status()

        self.store()
        self.log("Data stored", f"Crawler {self.id}")

        self.traversed.clear()
        self.log("Crawler killed", f"Crawler {self.id}")

        self.log("closing connection...")
        self.running = False
        
        for thread in self.threads:
            thread.join()
        
        self.log("threads closed", f"Crawler {self.id}")
        
        self.send("close,0")
        self.client.close()
        self.log("close client success")

    def send(self, message):
        message = str(message).encode()
        self.client.send(message)
        self.log(f"sent {message}")
    
    def status(self):
        self.log("Status requested", f"Crawler {self.id}")
        status = f"status,ID-{self.id},URL-{self.url},RUNNING-{self.running},TRAVERSED-{len(self.traversed)},QUEUE-{len(self.queue)}"
        self.log(status)
        self.send(status)

    def skip(self):
        pass

class Storage:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}

    def add(self, key, value):
        self.data[key] = value

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f)


crawler = Crawler(server_port=9999)
try:
    crawler.connect()
except:
    print("Unexpected error occured")
