import socket
import threading

HOST = socket.gethostname()
PORT = 8820

class create_socket():

    def __init__(self):

        self.server_socket = socket.socket()
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()

        self.clients = []

    def broadcast(self, data):
        for client in self.clients:
            client.send(data.encode('utf-8'))

    def receive(self):

        while(True):

            self.client, self.address = self.server_socket.accept()
            self.clients.append(self.client)

            thread = threading.Thread(target = self.handle, args = (self.client,))
            thread.start()

    def handle(self, client):

        while(True):
            data = str(client.recv(1024).decode())
            self.broadcast(data)

server_socket = create_socket()
print('server running...')
server_socket.receive()
