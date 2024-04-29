import socket
import threading

class create_socket():

    def __init__(self):
        self.client_socket = socket.socket()

    def connect_to_server(self):
        self.client_socket.connect(('192.168.1.41', 6969))

    def get_data(self):
        return self.client_socket.recv(1024).decode()

    def send_data(self):

        while(True):
            data = input('write a message: ')
            self.client_socket.send(data.encode())

    def close_server(self):
        self.client_socket.close()

def socket_procces():

    client_socket = create_socket()
    client_socket.connect_to_server()

    thread = threading.Thread(target = client_socket.send_data)
    thread.start()

    run = True
    while(run):
        print('nadav: ' + client_socket.get_data())
    client_socket.close_server()
