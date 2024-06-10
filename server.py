import socket
import threading
import mysql.connector
from datetime import datetime
import time
import hashlib
import rsa

host_name = socket.gethostname()
HOST = socket.gethostbyname(host_name)
print(HOST)
HOST='0.0.0.0'
PORT = 8821

# keys
public_key, private_key = rsa.newkeys(1024)
public_partner = None

messages_id_list = []

users_data_base = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nadavsh2006!",
    database="Mychat",
    auth_plugin='mysql_native_password'
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

                decrypted = False
                while (not decrypted):
                    try:
                        decrypted_info = rsa.decrypt(data, private_key)
                        decrypted = True

                    except:
                        pass

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

                        query = "SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1"
                        users_data_base_cursor.execute(query)

                        id = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                        id = id[0]

                        data = f'{check}`{id}'
                        self.client.send(data.encode('utf-8'))

                        print(f'/new_register {info[0]}')
                        self.broadcast(f'/new_register {info[0]}', client)
                    
                    case 'false':
                        self.client.send(check.encode('utf-8'))

            elif (data).startswith(b'/logged_in '):

                data = data.strip(b'/logged_in ')

                decrypted = False
                while (not decrypted):
                    try:
                        decrypted_info = rsa.decrypt(data, private_key).decode()
                        decrypted = True

                    except:
                        pass

                info = decrypted_info.split('`')

                password = info[1].encode('utf-8')
                password = hashlib.sha256(password).hexdigest()

                check ='false'
                nickname = ''
                id = ''

                query = f"SELECT * FROM users WHERE user_name = '{info[0]}' AND password = '{password}'"
                users_data_base_cursor.execute(query)
                
                row_count = users_data_base_cursor.rowcount
                if row_count != 0:
                    check = 'true'
                    for user in users_data_base_cursor:
                        nickname = user[3]
                        id = user[0]

                data = (f'{check}`{nickname}`{id}')
                client.send(data.encode('utf-8'))

            elif (data.decode()).startswith('/get_contacts '):
                sign = '/get_contacts '

                data = data.decode()
                data = data[len(sign):]
                id = int(data)

                all_contacts = ''

                query = f"SELECT * FROM mychat.contacts inner join mychat.users on contacts.contact_user_id = users.user_id where contacts.user_id = {id}"
                users_data_base_cursor.execute(query)

                for contact in users_data_base_cursor:
                    all_contacts += contact[8] + ' '
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

                query = f"SELECT user_id FROM users WHERE nick_name = '{passive_user}'"
                users_data_base_cursor.execute(query)

                passive_user_id = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                passive_user_id = passive_user_id[0]

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

                query = f"SELECT user_id FROM users WHERE nick_name = '{reciever_user}'"
                users_data_base_cursor.execute(query)

                reciever_user_id = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                reciever_user_id = reciever_user_id[0]

                users_data_base_cursor.execute("INSERT INTO messages_info (message_text_info, sender_id, reciever_id) VALUES (%s, %s, %s)",
                                               (data[1], sender_user_id, reciever_user_id))
                users_data_base.commit()

                query = f"SELECT last_message_id FROM mychat.contacts WHERE user_id = {sender_user_id} AND contact_user_id = {reciever_user_id}"
                users_data_base_cursor.execute(query)

                last_message_id = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                last_message_id = last_message_id[0]

                users_data_base_cursor.execute(f"UPDATE mychat.contacts SET last_message_id = {last_message_id} WHERE user_id = {sender_user_id} AND contact_user_id = {reciever_user_id}")
                users_data_base.commit()

            elif (data.decode()).startswith('/recieve_message '):

                data = data.decode()
                data = data.split('`')

                user_id = int(data[1])

                contact_nickname = data[2]
                contact_id = 0

                counter = 0

                query = f"SELECT user_id FROM users WHERE nick_name = '{contact_nickname}'"
                users_data_base_cursor.execute(query)

                contact_id = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                contact_id = contact_id[0]

                query = f"SELECT last_message_id FROM contacts WHERE user_id = {user_id} AND contact_user_id = {contact_id}"
                users_data_base_cursor.execute(query)

                counter = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                counter = counter[0]

                messages = ''
                last_message_id = 0

                query = f"SELECT * FROM messages_info WHERE reciever_id = {user_id} AND sender_id = {contact_id}"
                users_data_base_cursor.execute(query)

                for message in users_data_base_cursor:
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

                    query = f"UPDATE mychat.contacts SET last_message_id = {last_message_id} WHERE user_id = {user_id} AND contact_user_id = {contact_id}"
                    users_data_base_cursor.execute(query)
                    users_data_base.commit()

            elif (data.decode()).startswith('/recieve_last_five_messages '):
                
                data = data.decode()
                data = data.split()
                user_id = int(data[1])

                last_five_messages = ''
                query = "SELECT user_id FROM mychat.users WHERE nick_name = '{}'".format(data[2])
                users_data_base_cursor.execute(query)

                contact_user_id = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                contact_user_id = contact_user_id[0]

                query = "SELECT last_message_id FROM mychat.contacts WHERE user_id = {} AND contact_user_id = {}".format(user_id, contact_user_id)
                users_data_base_cursor.execute(query)

                last_message_id = [int(record[0]) for record in users_data_base_cursor.fetchall()]
                last_message_id = last_message_id[0]

                counter = 5

                query = f"(SELECT * FROM mychat.messages_info WHERE (sender_id = {user_id} AND reciever_id = {contact_user_id}) OR (sender_id = {contact_user_id} AND reciever_id = {user_id}) ORDER BY message_id DESC)"
                users_data_base_cursor.execute(query)
                for message in users_data_base_cursor:

                    if counter == 0:
                        break

                    if message[0] <= last_message_id:

                        now = str(message[4])
                        if message[2] == user_id and message[3] == contact_user_id:
                            last_five_messages += f'{message[1]} {now[:-3]} (you)'
                            counter -= 1
                            last_five_messages += '/separation/'

                        elif message[2] == contact_user_id and message[3] == user_id:
                            last_five_messages += f'{message[1]} {now[:-3]} ({data[2]})'
                            counter -= 1
                            last_five_messages += '/separation/'

                last_five_messages = last_five_messages[:-12]
                print(last_five_messages)
                client.send(f'/recieve_last_five_messages {last_five_messages}'.encode('utf-8'))

server_socket = create_socket()
print('server running...')
server_socket.receive()
