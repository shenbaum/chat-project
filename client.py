import socket
import threading
from tkinter import ttk
from tkinter import *
from datetime import datetime
from tkinter.messagebox import askyesno
import time
from customtkinter import *
import rsa
from classes import *

HOST, PORT = '10.64.109.60', 8821

#colours
colour_1 = '#3CB371'
colour_2 = '#05d7ff'
colour_3 = '#123521'
colour_4 = 'BLACK'

public_partner = None

hostname = socket.gethostname()
my_ip_address = socket.gethostbyname(hostname)

column = 0

chat_gui = False
chat_is_on = False
can_double_click = True

nickname = ''
id = '0'

logged_in = 'false'

class create_client():

    def __init__(self, HOST, PORT):
        global public_partner

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.running = True
        self.current_chat = ''

        public_partner = rsa.PublicKey.load_pkcs1(self.client_socket.recv(1024))

        self.all_users_lisl = ''

        self.all_users = self.client_socket.recv(2048).decode()
        if self.all_users != 'no_users':
            self.all_users_list = self.all_users.split('/')

        login_and_register_screen(self.client_socket)

        if logged_in == 'false':
            self.close_program()

        else:

            data = f'/get_contacts `{id}'
            self.client_socket.send(data.encode('utf-8'))

            self.my_contacts_list_and_dates = self.client_socket.recv(2048).decode()
            self.my_contacts_nicknames_list = []


            if self.my_contacts_list_and_dates != 'false':
                self.my_contacts_list_and_dates = self.my_contacts_list_and_dates.split('/separation/')

                for nickname in self.my_contacts_list_and_dates:
                    self.my_contacts_nicknames_list.append(nickname.split()[0])

            else:
                self.my_contacts_list_and_dates = []

            self.receive_thread = threading.Thread(target = self.receive)
            self.main_tabs_screen_thread = threading.Thread(target = self.main_tabs_screen)

            self.receive_thread.start()
            self.main_tabs_screen_thread.start()

    def receive(self):

        while(self.running):

            data = self.client_socket.recv(1024).decode()

            if data.startswith('/new_register '):
                sign = '/new_register '

                user_nickname = data[len(sign):]

                if not user_nickname in self.all_users_list:
                    if user_nickname != nickname:
                        self.all_users_list.append(user_nickname)
                        users_list.insert(END, user_nickname)

            elif data.startswith('/new_friendship '):

                data = data.split()

                if nickname in data:

                    if data[2] == nickname:

                        self.my_contacts_nicknames_list.append(data[1])

                        new_contact = self.my_contacts_nicknames_list[-1]

                        date_time = datetime.now()
                        now = date_time.strftime("%d/%m/%Y %H:%M:%S")

                        nickname_time = f'{new_contact} {now}'
                        self.my_contacts_list_and_dates.append(nickname_time)

                        replaced_time = (str(now).split()[0]) + '_' + (str(now).split()[1])

                        contacts_table.insert(parent = '', index = 'end',
                                iid = self.my_contacts_list_and_dates.index(nickname_time),
                                text = new_contact, values = replaced_time[:-3])
                        
                        self.insert_contacts_list(self.all_users_list)

                        message_box(f'{new_contact} added you to his/her contacts!', 'info')

            elif data.startswith('/recieve_message '):
                sign = '/recieve_message '

                data = data[len(sign):]
                if data != '':

                    messages = data.split('/separation/')

                    if chat_is_on:
                        text_widget.configure(state = 'normal')
                        text_widget.configure(text_color = colour_3)

                        for message in messages:
                            text_widget.insert(INSERT, f'{message} ({selected_contact})\n')
                        text_widget.configure(state = 'disabled')

            elif data.startswith('/recieve_last_five_messages '):
                sign = '/recieve_last_five_messages '

                if chat_is_on:

                    messages = data[len(sign):]

                    messages = messages.split('/separation/')
                    messages.reverse()

                    text_widget.configure(state = 'normal')

                    text_widget.insert(END, f'The last five messages -\n')

                    for message in messages:
                        if '(you)' in message:
                            text_widget.configure(text_color = colour_1)
                            text_widget.insert(END, f'{message}\n')

                        else:
                            text_widget.configure(text_color = colour_3)
                            text_widget.insert(END, f'{message}\n')

                    text_widget.insert(END, f'new messages -\n')

                    text_widget.configure(state = 'disabled')

    def close_program(self):
        self.running = False
        self.client_socket.close()
        exit(0)

#my contacts screen

    def main_tabs_screen(self):
        global contacts_table, win, my_contact_gui, add_new_contact_gui, users_list, search_entry, my_tab

        win = CTk()
        win.geometry("750x420+585+330")
        win.title('Mychat')

        my_tab = CTkTabview(win, corner_radius = 10, height = 420)
        my_tab.pack(pady = 10)

        my_contacts_tab = my_tab.add('My Contacts')
        add_contact_tab = my_tab.add('Add_Contact')

        #my contacts tab

        title = CTkLabel(my_contacts_tab, text ='My Contacts', font = CTkFont(size = 30, weight = 'bold'))
        title.pack(pady = 5)

        table_style = ttk.Style()
        table_style.theme_use('clam')
        table_style.configure('Treeview',
                background = '#2B2B2B',
                foreground = 'white',
                fieldbackground = '#343638'
                )
        
        table_style.map('Treeview', background = [('selected', '#343638')])
        
        table_style.configure('Treeview.Heading',
                background = '#2B2B2B',
                foreground = colour_1,
                relief = 'flat'
        )

        table_style.map('Treeview.Heading', background = [('selected', '#343638')])
        
        table_style.configure('Treeview', highlightthickness = 0, bd = 0, font = (CTkFont, 11))
        table_style.configure('Treeview.Heading', font = (CTkFont, 13, 'bold'))
        table_style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])

        table_frame = CTkFrame(my_contacts_tab, height = 400, width = 350, corner_radius = 26)
        table_frame.pack(pady = 5)

        contacts_table = ttk.Treeview(table_frame, style = 'Treeview')

        contacts_table['columns'] = ('Time-Added')

        contacts_table.column('#0')
        contacts_table.column('Time-Added')

        contacts_table.heading('#0', text = 'Contacts', anchor = W)
        contacts_table.heading('Time-Added', text = 'Time-Added', anchor = W)

        contacts_table.pack()

        log_out_button = create_button(my_contacts_tab, 'Exit', CTkFont, 30, 260, self.logged_out, ())
        log_out_button = log_out_button.putinfo()
        log_out_button.pack(pady = 5)

        self.insert_my_contacts()

        contacts_table.bind('<Double-Button-1>', self.chat_screen)

        #add contact tab

        title_label = CTkLabel(add_contact_tab, text ='Add New Contact', font = CTkFont(size = 30, weight = 'bold'))
        title_label.pack(pady = 10)

        search_entry = CTkEntry(add_contact_tab, placeholder_text = 'Search for new contacts..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        search_entry.pack(pady = 10)

        users_list = Listbox(add_contact_tab, height = 8, width = 50, font = CTkFont(size = 14, weight = 'normal'),
                             background = '#2A2D2E', foreground = colour_1)
        users_list.pack()

        list_style = ttk.Style()
        list_style.theme_use('clam')
        list_style.configure('user_list',
                background = '#2A2D2E',
                foreground = 'white',
                fieldbackground = '#343638'
                )
        
        list_style.map('user_list', background = [('selected', '#343638')])
        

        add_button = create_button(add_contact_tab, 'Add', CTkFont, 30, 260, self.add_new_contact_db, ())
        add_button = add_button.putinfo()
        add_button.pack(pady = 30)

        self.insert_contacts_list(self.all_users_list)
        search_entry.bind("<KeyRelease>", self.create_contacts_list)

        win.mainloop()

#my contacts min func

    def insert_my_contacts(self):

        for contact in self.my_contacts_list_and_dates:
            data = contact.split()
            data[1] += '_'
            contacts_table.insert(parent = '', index = 'end', iid = self.my_contacts_list_and_dates.index(contact), text = data[0], values = data[1] + data[2][:-3])

    def logged_out(self):
        win.destroy()
        self.close_program()

#add new contact min func

    def add_new_contact_db(self):
        global add_new_contact_gui

        selected_contact = users_list.curselection()

        if selected_contact:

            date_time = datetime.now()
            now = date_time.strftime("%d/%m/%Y %H:%M:%S")

            selected_contact = users_list.get(ANCHOR)

            self.client_socket.send(f'/new_friendship `{id}`{selected_contact}`{nickname}'.encode('utf-8'))

            self.my_contacts_list_and_dates.append(f'{selected_contact} {now}')
            self.my_contacts_nicknames_list.append(selected_contact)

            self.insert_contacts_list(self.all_users_list)

            contacts_table.insert(parent = '', index = 'end', iid = self.my_contacts_list_and_dates.index(f'{selected_contact} {now}'), text = selected_contact, values = now)

            message_box(f'{selected_contact} successfuly added!', 'info')

    def create_contacts_list(self, e):

        typed = search_entry.get()

        if typed == '':
            data = self.all_users_list

        else:
            data = []
            for contact in self.all_users_list:
                if typed.lower() in contact.lower():
                    data.append(contact)

        self.insert_contacts_list(data)

    def insert_contacts_list(self, data):

        users_list.delete('0', END)

        for contact in data:
            if not contact in self.my_contacts_nicknames_list:
                if contact != nickname:
                    users_list.insert(END, contact)

#chat screen

    def chat_screen(self, e):
        global can_double_click, msg_entry, selected_contact, text_widget, chat_is_on, my_contact_gui, add_new_contact_gui

        if can_double_click:

            can_double_click = False
            
            my_contact_gui = False
            add_new_contact_gui = False

            selected_contact = ''
            selected_contact = contacts_table.focus()
            selected_contact = contacts_table.item(selected_contact)
            selected_contact = selected_contact.get('text')

            if selected_contact != '':
                self.current_chat = selected_contact
                
                if chat_is_on:
                    my_tab.delete('Chat')

                chat_tab = my_tab.add('Chat')

                # head label
                head_label = CTkLabel(chat_tab, text = f'Mychat - {selected_contact}', font = CTkFont(size = 20, weight = 'bold'))
                head_label.pack()

                # text widget
                text_widget = CTkTextbox(chat_tab, width=500, height=260, font = CTkFont(size = 12, weight = 'bold'), 
                                text_color = colour_1, corner_radius = 10, activate_scrollbars = True,
                                scrollbar_button_hover_color = colour_1, border_width = 4, border_color = colour_1,
                                border_spacing = 16, wrap = 'word')
                text_widget.pack(pady = 5)
                text_widget.configure(state = "disabled")

                # message entry box
                msg_entry = CTkEntry(chat_tab, placeholder_text = 'Write a message..', width = 300, height = 34, text_color = colour_1, font = CTkFont(size = 14, weight = 'bold'))
                msg_entry.place(x = 10, y = 305)

                # send button
                send_button = create_button(chat_tab, 'Send', CTkFont, 20, 140, self.send_message, ())
                send_button = send_button.putinfo()
                send_button.place(x = 358, y = 307)

                chat_is_on = True

                self.client_socket.send(f'/recieve_last_five_messages {id} {selected_contact}'.encode('utf-8'))

                can_double_click = True

                recieve_messages_thread = threading.Thread(target = self.recieve_message, args = (selected_contact,))
                recieve_messages_thread.start()

    def send_message(self):
        
        if msg_entry.get() != '':

            now = datetime.now()
            now = now.strftime("%Y/%m/%d %H:%M")

            my_message = msg_entry.get()

            data = f'/new_message `{my_message}`{id}`{selected_contact}'
            self.client_socket.send(data.encode('utf-8'))

            text_widget.configure(state = 'normal')
            text_widget.configure(text_color = colour_1)
            text_widget.insert(INSERT, f'{my_message} {now.split()[0]}_{now.split()[1]} (you)\n')
            msg_entry.delete('0', END)
            text_widget.configure(state = 'disabled')

    def recieve_message(self, selected_contact):

        while(chat_is_on):
            self.client_socket.send(f'/recieve_message `{id}`{selected_contact}'.encode('utf-8'))

            check = self.current_chat
            time.sleep(3)
            if check != self.current_chat:
                break

#friend request screen

    def friend_request_screen(self):
        global friend_request_list

        root = CTk()
        root.geometry("750x420+585+330")
        root.title('Mychat')

        title = CTkLabel(root, text ='Friend Requests', font = CTkFont(size = 30, weight = 'bold'))
        title.pack(pady = 10)

        friend_request_list = Listbox(root, height = 8, width = 50, font = CTkFont(size = 14, weight = 'normal'),
                             background = '#2A2D2E', foreground = colour_1)
        friend_request_list.pack()

        list_style = ttk.Style()
        list_style.theme_use('clam')
        list_style.configure('user_list',
                background = '#2A2D2E',
                foreground = 'white',
                fieldbackground = '#343638'
                )
        
        list_style.map('friend_request_list', background = [('selected', '#343638')])

        table_frame = CTkFrame(root, height = 400, width = 350, corner_radius = 26)
        table_frame.pack(pady = 15)

        contacts_table = ttk.Treeview(table_frame, style = 'Treeview')

        contacts_table.column('#0')

        contacts_table.heading('#0', text = 'Requests', anchor = W)

        contacts_table.pack()

        #add_contact_button = create_button(root, 'Accept', CTkFont, 30, 260, pass, ())
        #add_contact_button = add_contact_button.putinfo()
        #add_contact_button.pack()

        log_out_button = create_button(root, 'Return', CTkFont, 30, 260, self.return_to_my_contacts_screen, ())
        log_out_button = log_out_button.putinfo()
        log_out_button.pack(pady = 10)

        self.insert_my_contacts()

        friend_request_gui = True

        root.mainloop()

#login/register

def login_and_register_screen(client_socket):
        global win, log_username_entry, log_password_entry, register_tab
        global reg_nickname_entry, reg_username_entry, reg_passwordA_entry, reg_passwordB_entry

        win = CTk()
        win.geometry("750x420+585+330")
        win.title('Login page')
        win.iconbitmap('loginlockrefreshincircularbutton_80241.ico')

        set_default_color_theme('green')

        my_tab =  CTkTabview(win, corner_radius = 10)
        my_tab.pack(pady = 10)

        login_tab = my_tab.add('Login')
        register_tab = my_tab.add('Register')

        #login tab

        log_username_label = CTkLabel(login_tab, text="Username", font = CTkFont(size = 30, weight = 'bold')).pack(pady = 15)
        log_username_entry = CTkEntry(login_tab, placeholder_text = 'Enter username..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        log_username_entry.pack(pady = 10)

        log_password_label = CTkLabel(login_tab, text="Password", font = CTkFont(size = 30, weight = 'bold')).pack()
        log_password_entry = CTkEntry(login_tab, placeholder_text = 'Enter password..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        log_password_entry.configure(show = '*')
        log_password_entry.pack(pady = 10)

        checkbox = CTkCheckBox(login_tab, text = "show password", fg_color = colour_1, 
                    checkbox_height = 20, checkbox_width = 20, corner_radius = 26, text_color = colour_1, command = show_password_login)
        checkbox.pack()

        login_frame = CTkFrame(login_tab, width = 500, height = 200)
        login_frame.pack(pady=35)

        login_button = create_button(login_frame, 'Login', CTkFont, 30, 260, loged_in, client_socket)
        login_button = login_button.putinfo()
        login_button.pack()

        #register tab

        reg_nickname_label = CTkLabel(register_tab, text="Nickname", font = CTkFont(size = 20, weight = 'bold')).pack(pady = 5)
        reg_nickname_entry = CTkEntry(register_tab, placeholder_text = 'Enter nickname..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_nickname_entry.pack(pady = 5)


        reg_usename_label = CTkLabel(register_tab, text="Username", font = CTkFont(size = 20, weight = 'bold')).pack(pady = 5)
        reg_username_entry = CTkEntry(register_tab, placeholder_text = 'Enter username..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_username_entry.pack(pady = 5)


        reg_password_label = CTkLabel(register_tab, text="Password", font = CTkFont(size = 20, weight = 'bold')).pack(pady = 5)

        reg_passwordA_entry = CTkEntry(register_tab, placeholder_text = 'Enter password..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_passwordA_entry.configure(show = '*')
        reg_passwordA_entry.pack(pady = 5)

        reg_passwordB_entry = CTkEntry(register_tab, placeholder_text = 'Confirm password..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_passwordB_entry.configure(show = '*')
        reg_passwordB_entry.pack(pady = 5)

        checkbox = CTkCheckBox(register_tab, text = "show password", fg_color = colour_1, 
                    checkbox_height = 20, checkbox_width = 20, corner_radius = 26, text_color = colour_1, command = show_password_register)
        checkbox.pack(pady = 5)

        submit_frame = CTkFrame(register_tab, width = 500, height = 200)
        submit_frame.pack(pady = 5)

        submit_button = create_button(submit_frame, 'Submit', CTkFont, 30, 260, submited, client_socket)
        submit_button = submit_button.putinfo()
        submit_button.pack()

        win.mainloop()

#login min func

def show_password_login():
    if log_password_entry.cget('show') == '':
        log_password_entry.configure(show='*')
    else:
        log_password_entry.configure(show='')

def GetLoginInfo():
        log_username = log_username_entry.get()
        log_password = log_password_entry.get()

        log_username_entry.delete(0, 'end')
        log_password_entry.delete(0, 'end')

        return log_username, log_password

def loged_in(client_socket):
        global logged_in, nickname, id

        check = 'false'
        contain_sign = False

        username, password = GetLoginInfo()
        if username != '' and password != '':

            for letter in username:
                if not letter.isdigit() and not letter.isalpha():
                    contain_sign = True
                    break
                
            for letter in password:
                if not letter.isdigit() and not letter.isalpha():
                    contain_sign = True
                    break

                
                if contain_sign:
                    break

            if not contain_sign:

                info = bytes(f'{username}`{password}', 'utf8')
                encrypted_info = rsa.encrypt(info, public_partner)
                
                client_socket.send('/logged_in '.encode('utf-8') + encrypted_info)

                check_nickname_id = client_socket.recv(1024).decode()
                check, nickname, id = check_nickname_id.split('`')

                match check:
                    case 'true':
                        logged_in = 'true'
                        message_box('You have been Connected successfully!', 'info')
                        win.destroy()

                    case 'false':
                        message_box('Invalid username or password', 'error')

            else:
                message_box('You cant have signs letters in your input!', 'error')

#register min func

def get_register_info():
        reg_nickname = reg_nickname_entry.get()
        reg_username = reg_username_entry.get()
        reg_passwordA = reg_passwordA_entry.get()
        reg_passwordB = reg_passwordB_entry.get()
        return reg_nickname, reg_username, reg_passwordA, reg_passwordB

def show_password_register():
        if reg_passwordA_entry.cget('show') == '*':
            reg_passwordA_entry.configure(show = '')
            reg_passwordB_entry.configure(show = '')
        else:
            reg_passwordA_entry.configure(show = '*')
            reg_passwordB_entry.configure(show = '*')

def submited(client_socket):
        global logged_in, nickname, id

        contain_sign = False

        check = False
        if get_register_info()[2] == get_register_info()[3]:
            if len(get_register_info()[2]) >= 8:
                if get_register_info()[2] != '':
                    if get_register_info()[1] != '':
                        if get_register_info()[0] != '':
                            for nickname in get_register_info()[0]:
                                if not nickname.isdigit() and not nickname.isalpha():
                                    contain_sign = True
                                    break

                        for username in get_register_info()[1]:
                            if not username.isdigit() and not username.isalpha():
                                contain_sign = True
                                break

                        for pass_one in get_register_info()[2]:
                            if not pass_one.isdigit() and not pass_one.isalpha():
                                contain_sign = True
                                break

                        for pass_two in get_register_info()[3]:
                            if not pass_two.isdigit() and not pass_two.isalpha():
                                contain_sign = True
                                break

                        if contain_sign:
                            message_box('You cant have signs letter in your input!', 'error')
                            check = None

                        else:
                            check = True

            else:
                message_box('Your password have to contain at least 8 letters!', 'info')
                check = None

        match check:
            case True:

                info = bytes(f"{get_register_info()[0]}`{get_register_info()[1]}`{get_register_info()[2]}", "utf-8")
                encrypted_info = rsa.encrypt(info, public_partner)

                client_socket.send('/registered '.encode('utf-8') + encrypted_info)

                data = client_socket.recv(1024).decode()
                data, id = data.split('`')

                if data == 'true':
                    logged_in = 'true'
                    nickname = get_register_info()[0]
                    message_box('You have been registered successfully!', 'info')
                    win.destroy()
                else:
                    message_box('Your nickname is already taken', 'error')

            case False:
                message_box('Info must match', 'error')


def message_box(string, sign):
    msg = create_message(sign, string)
    msg.show()


client_socket = create_client(HOST, PORT)
