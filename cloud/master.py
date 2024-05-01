import socket
import threading
from logger import Logger

# sudo lsof -ti :9999 | xargs --no-run-if-empty kill


class Server:
    def __init__(self, host="0.0.0.0", port=9999, clients = 5):
        self.host = host
        self.port = port
        self.num_clients = clients
        self.running = False
        self.server = None
        self.nodes = []
        self.clients = []
        self.connection = None
        self.logger = Logger(show_logs=True, author="Ph-Master")
        self.log = self.logger.log

    def handle_client(self, client_socket):
        raddr = client_socket.getpeername()
        self.log(f"listening to : {raddr[1]}", "<handle_client>")
        while self.running:
            request = client_socket.recv(1024)
            self.log(f"{raddr[1]}: {request}", "<handle_client>")

            request = request.decode().split(",")
            
            action = request[0]
            if action == "close":
                self.log(f"{raddr[1]} request closure", "<handle_client>")
                self._close_client(raddr[1])
                break
            else:
                client_socket.send(b"ACK!")

        client_socket.close()
        self.log("Connection closed", "<handle_client>")

    def _close_client(self, id):
        self.log(f"Closing client {id}")
        index = self.nodes.index(id)
        self.nodes.pop(index)
        self.clients.pop(index)

    def status(self):
        self.log("status requested", "<status>")
        self.log(f"Nodes: {self.nodes}", "<status>")
        for node in self.nodes:
            self.log(f"Requesting status from {node}")
            self.send_message("status", node)
    
    def send_message(self, message, address):
        self.log(f"Sending message to {address}")
        index = self.nodes.index(address)
        self.clients[index].send(message.encode())
    
    def _broadcast(self, message):
        self.log(f"broadcasting message : {message}")
        
        for client in self.clients:
            client.send(message.encode())

    def run(self):
        self.log("Starting the server", "<run>")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.server.settimeout(1)
        self.log(f"accepting {self.num_clients} clients", "<run>")
        self.log(f"Listening on port {self.port}", "<run>")

        while self.running:
            # print("<run()> : current status : ", self.running)
            try:
                client, addr = self.server.accept()
                self.nodes.append(addr[1])
                self.clients.append(client)
                self.log(f"Accepted connection from: {addr[0]}:{addr[1]}")
                client_handler = threading.Thread(target=self.handle_client, args=(client,))
                client_handler.start()
            except socket.timeout:
                # self.log("Timeout", "<run>")
                continue
        
        self.log("server loop exit, waiting for closing", "<run>")

    def start(self):
        self.running = True
        self.connection  = threading.Thread(target=self.run)
        self.log("Starting the connection ", "<start>")
        self.connection.start()

        while True:
            command = input("Enter the command : ")
            if command == "status":
                self.status()
            elif command == "broadcast":
                msg = input("Enter the broadcast msg : ")
                self._broadcast(msg)
            elif command == "stop":
                break
            else:
                print("Invalid command")
        
        print("server stop issued", "<start>")
        self.stop()
        

    def stop(self):
        print(self.nodes)
        self.running = False
        self.log("running => false", "<stop>")

        if self.connection:
            self.log("stopping connection", "<stop>")
            self.connection.join()
            self.log("connection closed", "<stop>")
        
        if self.server:
            self.log("server closing", "<stop>")
            self.server.close()
            self.log("server closed", "<stop>")
        
        self.log("service stopped")

server = Server(port=9999)
try:
    server.start()
except:
    print("Error occured!, closing the server")
    server.stop()