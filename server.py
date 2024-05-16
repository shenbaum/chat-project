import socket
import threading
from cryptography.fernet import Fernet

HOST = socket.gethostname()
PORT = 8820

with open('mykey.key', 'rb') as mykey:
    key = mykey.read()

f = Fernet(key)

class create_socket():

    def __init__(self):

        self.server_socket = socket.socket()
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()

        self.clients = []
        self.nicknames = []

    def broadcast(self, data):
        for client in self.clients:
            client.send(data.encode('utf-8'))

    def receive(self):

        while(True):

            self.client, self.address = self.server_socket.accept()
            nickname = str(self.client.recv(1024).decode())
            self.clients.append(self.client)
            self.nicknames.append(nickname)

            thread = threading.Thread(target = self.handle, args = (self.client,))
            thread.start()

    def handle(self, client):

        while(True):

            data = client.recv(1024).decode()

            if data.startswith('/message '):
                try:
                    data = data.strip('/message ') # /message yoni hey buddy^nadav^ip
                    reciever_nickname = data.partition(' ')[0]

                    for nickname in self.nicknames:
                        if nickname == reciever_nickname:

                            index = self.nicknames.index(reciever_nickname)
                            data = data.replace(' ', '^', 1) #yoni^hey buddy^nadav^ip
                            self.clients[index].send(data.encode('utf-8'))

                            client.send(data.encode('utf-8'))

                            break
                except:
                    print("Something went wrong")

            elif data.startswith('registered '):
                with open('enc_info.csv', 'ab') as file:
                    encrypted_info = data.split()
                    decrypted_info = f.decrypt(encrypted_info[1])

                    file.write(decrypted_info + b'\n')
                    file.close()

            elif data.startswith('logged-in '):
                with open('enc_info.csv', 'rb') as file:
                    encrypted_info = data.split()
                    decrypted_info = f.decrypt(encrypted_info[1]) + b'\n'

                    check ='false'
                    lines = file.readlines()

                    for line in lines:
                        if decrypted_info == line:
                            check = 'true'
                            break

                    client.send(check.encode('utf-8'))

            else:
                self.broadcast(data)

server_socket = create_socket()
print('server running...')
server_socket.receive()
