"""
Master crawler
"""

import socket
import threading
from ..utils.logger import Logger
import os
import json

# sudo lsof -ti :9999 | xargs --no-run-if-empty kill


class Server:
    def __init__(self, host="0.0.0.0", port=9999, clients=5, burnout=1000):
        self.host = host
        self.port = port
        self.num_clients = clients
        self.running = False
        self.server = None
        self.nodes = []
        self.clients = []
        self.connection = None
        self.logger = Logger(show_logs=True, author="master_node-Server")
        self.log = self.logger.log
        self.CLI_MODE = True
        self.burnout = burnout
        self.statuses = {}

    def handle_client(self, client_socket):
        raddr = client_socket.getpeername()
        self.log(f"listening to : {raddr[1]}", origin="<handle_client>")
        while self.running:
            request = client_socket.recv(1024)
            self.log(f"{raddr[1]}: {request}", origin="<handle_client>")

            request = request.decode().split(",")

            action = request[0]
            if action == "close":
                self.log(f"{raddr[1]} request closure", origin="<handle_client>")
                self._close_client(raddr[1])
                break
            if action == "status":
                self.log(f"{raddr[1]} responded status", origin="<handle_client>")
                self.statuses[raddr[1]] = request[1:]
            else:
                client_socket.send(b"ACK!")

        client_socket.close()
        self.log("Connection closed", origin="<handle_client>")

    def _close_client(self, addr):
        self.log(f"Closing client {addr}", origin="<close_client>")
        index = self.nodes.index(addr)
        self.nodes.pop(index)
        self.clients.pop(index)

    def _get_status(self, address):
        index = self.nodes.index(address)
        client = self.clients[index]
        message = "status"
        client.send(message.encode())
        self.log(f"Requesting status from {address}", origin="<get_status>")

    def status(self):
        self.log("status requested", origin="<status>")
        self.log(f"Nodes: {self.nodes}", origin="<status>")
        for node in self.nodes:
            self.log(f"Requesting status from {node}", origin="<status>")
            self.send_message("status", node)

    def send_message(self, message, address):
        self.log(f"Sending message to {address}",origin="send_message")
        index = self.nodes.index(address)
        try:
            self.clients[index].send(message.encode())
        except:
            self.logger.error(
                "Error occured while sending message", "master-send-message"
            )
            self._close_client(address)

    def _broadcast(self, message):
        self.log(f"broadcasting message : {message}", origin="broadcast")

        for client in self.clients:
            client.send(message.encode())

    def assign_sites(self, remove_exist=True):
        if remove_exist:
            count = 0
            if len(self.sites) < len(self.nodes):
                # repeat the sites
                for node in self.nodes:
                    self._set_up(node, self.sites[count])
                    count += 1
                    count = count % len(self.sites)
            else:
                for node in self.nodes:
                    self._set_up(node, self.sites[count])
                    count += 1

                while count < len(self.sites):
                    self._add_site(
                        self.nodes[count % len(self.nodes)], [self.sites[count]]
                    )
                    count += 1
        else:
            count = 0
            self.status()

            for node, stat in zip(self.nodes, self.statuses):
                if stat[1].split("-")[1] == "None":
                    self._set_up(node, self.sites[count])
                    count += 1
                    count = count % len(self.sites)
                else:
                    self._add_site(node, [self.sites[count]])
                    count += 1

    def generate(self):
        self.log("Generating the sites", origin="generate")
        if self.CLI_MODE:
            self.sites = input("Enter the sites saperated by commas : ").split(",")

        if not self.sites:
            self.log("No sites present", origin="generate")
            return
        self.assign_sites()

        self.log("Generated the sites", origin="generate")
        # now crawling them,

        for node in self.nodes:
            self._run(node)

        self.log("crawling started", origin="generate")

    def _run(self, address):
        index = self.nodes.index(address)
        client = self.clients[index]

        message = f"crawl"
        client.send(message.encode())

        self.log(f"set-up for {address}", origin="_run")

    def _set_up(self, address, site):
        index = self.nodes.index(address)
        client = self.clients[index]

        message = f"setup,{site},{self.burnout}"
        client.send(message.encode())

        self.log(f"set-up for {address}", origin="_set_up")

    def _add_site(self, address, sites):
        index = self.nodes.index(address)
        client = self.clients[index]

        if len(sites) < 1:
            self.log("cannot append less than 1 site", origin="add_site")
            return

        message = f"append"
        for site in sites:
            message += f",{str(site)}"
        client.send(message.encode())

        self.log(f"Add {len(sites)} sites for {address}", origin="add_site")

    def run(self):
        self.log("Starting the server", origin="<run>")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.server.settimeout(1)
        self.log(f"accepting {self.num_clients} clients", origin="<run>")
        self.log(f"Listening on port {self.port}", origin="<run>")

        while self.running:
            # print("<run()> : current status : ", self.running)
            try:
                client, addr = self.server.accept()
                self.nodes.append(addr[1])
                self.clients.append(client)
                self.log(f"Accepted connection from: {addr[0]}:{addr[1]}", origin="<run>")
                client_handler = threading.Thread(
                    target=self.handle_client, args=(client,)
                )
                client_handler.start()
            except socket.timeout:
                continue

        self.log("server loop exit, waiting for closing", origin="<run>")

    def start(self):
        try:

            self.running = True
            self.connection = threading.Thread(target=self.run)
            self.log("Starting the connection ", origin="<start>")
            self.connection.start()

            while True:
                command = input("Enter the command : ")
                if command == "status":
                    self.status()
                elif command == "broadcast":
                    msg = input("Enter the broadcast msg : ")
                    self._broadcast(msg)
                elif command == "send":
                    print("Nodes : ", self.nodes)
                    node = int(input("Enter the id of node : "))
                    msg = input("Enter the message : ")
                    self.send_message(msg, node)
                elif command == "stop":
                    break
                elif command == "generate":
                    self.generate()
                elif command == "run":
                    self._run()
                elif command == "assignAll":
                    self.assign_sites()
                elif command == "assign":
                    self.assign_sites(False)
                elif command == "add":
                    print("nodes : ", self.nodes)
                    site = input("Enter the sites saperated by comma : ").split(",")
                    node = int(input("Enter the node id : "))
                    self._add_site(node, [site])
                elif command == "setup":
                    site = input("Enter the site : ")
                    node = int(input("Enter the node id : "))
                    self._set_up(node, site)
                elif command == "merge":
                    self.merge()
                else:
                    print("Invalid command")

            print("server stop issued", "<start>")
            self.stop()
        except:
            self.logger.error("Error occured while starting the server", "master-start")
            self.stop()

    def merge(self):
        index_data = {}
        titles_data = {}
        files_to_delete = []
        self.log("merging the data", origin="<merge>")
        for filename in os.listdir("."):
            if filename.startswith("index"):
                with open(filename, "r") as f:
                    data = json.load(f)
                    index_data.update(data)
                files_to_delete.append(filename)
            elif filename.startswith("title"):
                with open(filename, "r") as f:
                    data = json.load(f)
                    titles_data.update(data)
                files_to_delete.append(filename)

        self.log("merging done", origin="<merge>")
        with open("index.json", "w") as f:
            json.dump(index_data, f)
        with open("titles.json", "w") as f:
            json.dump(titles_data, f)
        self.log("merged data saved", origin="<merge>")

        # Delete the files
        for filename in files_to_delete:
            os.remove(filename)
        self.log("old files deleted", origin="<merge>")

    def stop(self):
        print(self.nodes)
        self.running = False
        self.log("running => false", origin="<stop>")

        for node in self.nodes:
            self.send_message("stop", node)

        if self.connection:
            self.log("stopping connection", origin="<stop>")
            self.connection.join()
            self.log("connection closed", origin="<stop>")

        if self.server:
            self.log("server closing", origin="<stop>")
            self.server.close()
            self.log("server closed", origin="<stop>")

        self.log("service stopped")


server = Server(port=9999)
server.start()
