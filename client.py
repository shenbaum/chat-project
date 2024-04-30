import socket
import threading
from logingui import *

hostname = socket.gethostname()
my_ip_address = socket.gethostbyname(hostname)

information = []
username = 'connected_username'
can_print = False

class create_socket():

    def __init__(self):
        self.client_socket = socket.socket()

    def connect_to_server(self):
        self.client_socket.connect(('192.168.1.41', 4242))

    def get_data(self):
        global can_print

        details = []
        for i in range(3):
            details.append(str(self.client_socket.recv(1024).decode()))
        information.append(details)
        can_print = True

    def send_data(self):
        global can_print

        while(True):

            message = input('enter a message: ')
            information.append([message, username, str(my_ip_address)])

            for detail in information[-1]:
                self.client_socket.send(detail.encode())
            can_print = True

    def close_server(self):
        self.client_socket.close()

client_socket = create_socket()
client_socket.connect_to_server()

thread = threading.Thread(target = client_socket.send_data)
thread.start()

thread_2 = threading.Thread(target = client_socket.get_data)
thread_2.start()

run = True
while(run):
    if can_print:
        for detail in information[-1]:
            print(detail)
        can_print = False
client_socket.client_socket()
