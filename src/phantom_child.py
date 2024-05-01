import socket
import threading
from logger import Logger
from .phantom_indexing import Parser
import time

class Child:
    def __init__(self, server_host="0.0.0.0", server_port=9999):
        self.server_host = server_host
        self.server_port = server_port

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.thread = None

        self.logger = Logger(show_logs=True, author="Ph-Child")
        self.log  = self.logger.log

        self.log(f"Child initialized to {self.server_host}:{self.server_port}")

    def connect(self):
        self.running = True
        self.client.connect((self.server_host, self.server_port))
        self.log("connected to server", "<connect>")
        self.thread = threading.Thread(target=self.listen_to_server)
        self.thread.start()
        self.log("thread started", "<connect>")

        while self.running:
            command = input("Enter command: ")
            if command == "stop":
                break
            elif command == "send":
                message = input("Enter message: ")
                child.send(message)
            else:
                print("Invalid command")

        self.log("closing connection", "<connect>")        
        self.close()

    def status(self):
        self.log(f"status : {self.running}")
        message = "status,"+str(int(self.running))
        self.client.send(message.encode())
        self.log("Status uploaded")

    def listen_to_server(self):
        self.log("Listening to server")
        self.client.settimeout(1)
        while self.running:
            try:
                response = self.client.recv(1024)
                self.log(f"Received: {response}")
                if response == b"status":
                    self.status()
                if response == b"stop":
                    self.log("close requested from server")
                    break
            except socket.timeout:
                continue
        
        self.running = False
        self.log("waiting to be closed")

    def send(self, message):
        message = str(message).encode()
        self.client.send(message)
        self.log(f"sent {message}")

    def close(self):
        self.log("closing connection...")
        self.running = False
        if self.thread is not None:
            self.thread.join()
        
        self.send("close,0")
        self.client.close()
        self.log("close client success")

class Crawler:
    def __init__(self, url, id, burnout=1000):
        self.id = id
        self.url = url
        self.running = True
        self.kill = False
        self.traversed = set()
        self.burnout = burnout
        self.log = Logger(show_logs=True, author=f"crawler-{id}").log
        self.local_urls = set()
        self.traversed = []
        self.queue = []
        self.parser = Parser(self.show_logs)
        self.start_time = time.time()

    def status(self):
        self.log("Status requested", f"Crawler {self.id}")
        status = f"Crawler {self.id} \n"
        status += "Status : {self.running} \n"
        status += f"Root : {self.url} \n"
        status += f"Traversed : {len(self.traversed)} \n"
        status += f"in-Queue : {len(self.queue)} \n"

        self.log(status, f"Crawler {self.id}")

    def crawl(self):
        self.log("Crawling started", f"Crawler {self.id}")
        self.queue.append(self.url)
        epoch = 0
        while self.queue and self.running:
            if time.time() - self.start_time > self.burnout:
                self.log("Burnout", f"Crawler {id}")
                break

            # if epoch % 100 == 0:
            #     self.status()
            #     local_urls = self.update_urls(local_urls, id)

            url = self.queue.pop(0)
            # clean the url
            url = self.parser.clean_url(url)

            if url in self.local_urls:
                self.log("Already scanned", f"Crawler {id}")
                continue

            self.local_urls.add(url)
            self.traversed.append(url)
            self.log(f"Traversing {url}", f"Crawler {id}")
            neighbors, content, url, title = self.parser.parse(url)
            self.store("storage", url, content)
            self.store("title", url, title)
            self.queue.extend(neighbors)
            # self.log(f"Neighbors {neighbors}", f"Crawler {id}")
            epoch += 1

        self.running = False
        self.log("Crawling stopped", f"Crawler {self.id}")

    def store(self,storage, key, val):
        pass

    def stop(self):
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



child = Child(server_port=9999)
try:
    child.connect()
except:
    print("could not connect to server")
