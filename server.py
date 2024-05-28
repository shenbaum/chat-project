import socket
import threading
import mysql.connector
from datetime import datetime
import time
import hashlib
import rsa

HOST = socket.gethostname()
PORT = 8820

# keys
public_key, private_key = rsa.newkeys(1024)
public_partner = None

messages_id_list = []

users_data_base = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nadavsh2006!",
    database="Mychat"
)

users_data_base_cursor = users_data_base.cursor(buffered=True)

class create_socket():

    def __init__(self):

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((HOST, PORT))
        self.server_socket.listen()

        self.clients = []

    def broadcast(self, data, sender):
        print(data)

        for client in self.clients:
            if client != sender:
                client.send(data.encode('utf-8'))

    def receive(self):

        while(True):

            self.client, self.address = self.server_socket.accept()
            self.clients.append(self.client)

            self.client.send(public_key.save_pkcs1('PEM'))

            all_users = ''
            users_data_base_cursor.execute("SELECT * FROM users")
            for user in users_data_base_cursor:
                all_users += user[3]
                all_users += '/'
            all_users = all_users[:-1]

            data = all_users
            
            if data == '':
                data = 'no_users'
            
            self.client.send(data.encode('utf-8'))

            thread = threading.Thread(target = self.handle, args = (self.client,))
            thread.start()

    def handle(self, client):

        while(True):

            data = client.recv(1024)

            if (data).startswith(b'/registered '):

                data = data.strip(b'/registered ')
                decrypted_info = rsa.decrypt(data, private_key)
                decrypted_info = decrypted_info.decode()
                info = decrypted_info.split('`')

                check = 'true'

                try:
                    users_data_base_cursor.execute("SELECT * FROM users")
                    for user in users_data_base_cursor:
                        if user[3] == info[0]:
                            check = 'false'
                
                except:
                    pass
                
                password = info[2].encode('utf-8')
                password = hashlib.sha256(password).hexdigest()

                match check:
                    case 'true':
                        
                        users_data_base_cursor.execute("INSERT INTO users (user_name, password, nick_name) VALUES ('{}', '{}', '{}')".format(info[1], password, info[0])
                        )
                        users_data_base.commit()

                        users_data_base_cursor.execute("SELECT user_id FROM users")
                        for user_id in users_data_base_cursor:
                            id = user_id[0]

                        data = f'{check}`{id}'
                        self.client.send(data.encode('utf-8'))

                        self.broadcast(f'/new_register {info[0]}', client)
                    
                    case 'false':
                        self.client.send(check.encode('utf-8'))

            elif (data).startswith(b'/logged_in '):

                data = data.strip(b'/logged_in ')
                decrypted_info = rsa.decrypt(data, private_key).decode()
                info = decrypted_info.split('`')

                password = info[1].encode('utf-8')
                password = hashlib.sha256(password).hexdigest()

                check ='false'
                nickname = ''
                id = ''
                
                try:

                    users_data_base_cursor.execute("SELECT * FROM users")
                    for user in users_data_base_cursor:
                        if user[1] == info[0] and user[2] == password:
                            check = 'true'
                            nickname = user[3]
                            id = user[0]
                            break
                
                except:
                    pass

                data = (f'{check}`{nickname}`{id}')
                client.send(data.encode('utf-8'))

            elif (data.decode()).startswith('/get_contacts '):

                data = data.decode()
                data = data.strip('/get_contacts `')
                id = int(data)

                all_contacts = ''
                qeury = f"SELECT * FROM mychat.contacts inner join users on contacts.contact_user_id=users.user_id where contacts.user_id={id}"
                users_data_base_cursor.execute(qeury)
                for contact in users_data_base_cursor:
                    all_contacts += contact[7] + ' '
                    all_contacts += str(contact[2])
                    all_contacts += '/separation/'
                all_contacts = all_contacts[:-12]

                if all_contacts != '':
                    client.send(all_contacts.encode('utf-8'))
                else:
                    client.send('false'.encode('utf-8'))

            elif (data.decode()).startswith('/new_friendship '):

                data = data.decode()
                data = data.split('`')

                active_user = data[3]
                active_user_id = int(data[1])

                passive_user = data[2]
                passive_user_id = ''

                users_data_base_cursor.execute("SELECT * FROM users")
                for user in users_data_base_cursor:
                    if passive_user == user[3]:
                        passive_user_id = user[0]

                users_data_base_cursor.execute("INSERT INTO contacts (user_id, contact_user_id, last_message_id) VALUES (%s, %s, %s)",
                                               (active_user_id, passive_user_id, 0))
                users_data_base.commit()

                users_data_base_cursor.execute("INSERT INTO contacts (user_id, contact_user_id, last_message_id) VALUES (%s, %s, %s)",
                                               (passive_user_id, active_user_id, 0))
                users_data_base.commit()

                self.broadcast(f'/new_friendship {active_user} {passive_user}', client)

            elif (data.decode()).startswith('/new_message '):

                data = data.decode()
                data = data.split('`')

                sender_user_id = int(data[2])

                reciever_user = data[3]

                users_data_base_cursor.execute("SELECT * FROM users")
                for user in users_data_base_cursor:
                    if reciever_user == user[3]:
                        reciever_user_id = int(user[0])

                users_data_base_cursor.execute("INSERT INTO messages_info (message_text_info, sender_id, reciever_id) VALUES (%s, %s, %s)",
                                               (data[1], sender_user_id, reciever_user_id))
                users_data_base.commit()

                users_data_base_cursor.execute("SELECT * FROM messages_info")
                for message in users_data_base_cursor:
                    last_message_id = int(message[0])

                users_data_base_cursor.execute(f"UPDATE mychat.contacts SET last_message_id = {last_message_id} WHERE user_id = {sender_user_id} AND contact_user_id = {reciever_user_id}")
                users_data_base.commit()

            elif (data.decode()).startswith('/recieve_message '):

                data = data.decode()
                data = data.split('`')

                user_id = int(data[1])

                contact_nickname = data[2]
                contact_id = 0

                counter = 0

                users_data_base_cursor.execute("SELECT * FROM users")
                for user in users_data_base_cursor:
                    if user[3] == contact_nickname:
                        contact_id = int(user[0])

                users_data_base_cursor.execute("SELECT * FROM contacts")
                for friendship in users_data_base_cursor:
                    if friendship[0] == user_id:
                        if friendship[1] == contact_id:
                            counter = friendship[3]

                messages = ''
                last_message_id = 0

                users_data_base_cursor.execute("SELECT * FROM messages_info")
                for message in users_data_base_cursor:
                    if message[3] == user_id:
                        if message[2] == contact_id:
                            if message[0] > counter:

                                messages += message[1]
                                messages += ' '

                                message_time = str(message[4])
                                messages += message_time[:-3]

                                messages += '/separation/'

                                last_message_id = int(message[0])

                if messages != '':

                    messages = '/recieve_message ' + messages[:-12]
                    client.send(messages.encode('utf-8'))

                    users_data_base_cursor.execute(f"UPDATE mychat.contacts SET last_message_id = {last_message_id} WHERE user_id = {user_id} AND contact_user_id = {contact_id}")
                    users_data_base.commit()

            elif (data.decode()).startswith('/recieve_last_five_messages '):
                
                data = data.decode()
                data = data.split()
                user_id = data[1]

                last_five_messages = ''

                users_data_base_cursor.execute(f"(SELECT * FROM messages_info ORDER BY message_id DESC LIMIT 5) ORDER BY message_id ASC")
                for message in users_data_base_cursor:
                    now = str(message[4])
                    if message[2] == user_id:
                        last_five_messages += f'{message[1]} {now[:-3]} (you)'

                    else:
                        last_five_messages += f'{message[1]} {now[:-3]} ({data[2]})'

                    last_five_messages += '/separation/'

                last_five_messages = last_five_messages[:-12]
                client.send(f'/recieve_last_five_messages {last_five_messages}'.encode('utf-8'))

server_socket = create_socket()
print('server running...')
server_socket.receive() 
