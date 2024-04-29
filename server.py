import socket
import threading

can_skip = False
(skipped_socket, skipped_address) = None, None

class create_socket():

    def __init__(self):
        self.server_socket = socket.socket()
        self.clients_addresses = []

    def accepting_user(self):

        self.server_socket.bind(('0.0.0.0', 6969))
        self.server_socket.listen()
        print('Server is up and running')

        (client_socket, client_address) = self.server_socket.accept()
        self.clients_addresses.append((client_socket, client_address))
        print('Client connected')

    def get_data(self):
        global skipped_socket, skipped_address, can_skip

        data = ''
        for client in self.clients_addresses:
            data = client[0].recv(1024).decode()
            if data != '':
                (skipped_socket, skipped_address) = client
                can_skip = True
                return data
            
    def send_data(self):

        data = str(self.get_data()).encode()

        if can_skip:
            for client in self.clients_addresses:
                if client != (skipped_socket, skipped_address):
                    client[0].send(data)

    def close_server(self):

        self.server_socket.close()

server_socket = create_socket()
thread = threading.Thread(target = server_socket.accepting_user)
thread.start()

run = True
while(run):
    server_socket.send_data()
server_socket.close_server()
