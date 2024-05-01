import socket
import threading
from logger import Logger

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

child = Child(server_port=9999)
try:
    child.connect()
except:
    print("could not connect to server")
