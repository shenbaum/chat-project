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

HOST, PORT = '192.168.1.41', 8820

#colours
colour_1 = '#3CB371'
colour_2 = '#05d7ff'
colour_3 = '#65e7ff'
colour_4 = 'BLACK'

public_partner = None

hostname = socket.gethostname()
my_ip_address = socket.gethostbyname(hostname)

column = 0

chat_gui = False
chat_is_on = False

add_new_contact_gui = False
my_contact_gui = False

nickname = ''
id = '0'

logged_in = 'false'

class create_client():

    def __init__(self, HOST, PORT):
        global public_partner

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.running = True

        public_partner = rsa.PublicKey.load_pkcs1(self.client_socket.recv(1024))

        self.all_users = self.client_socket.recv(2048).decode()
        if self.all_users != 'no_users':
            self.all_users_list = self.all_users.split('/')

        login_screen(self.client_socket)

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
            self.mycontacts_screen_thread = threading.Thread(target = self.mycontacts_screen)

            self.receive_thread.start()
            self.mycontacts_screen_thread.start()

    def receive(self):

        while(self.running):

            data = self.client_socket.recv(1024).decode()
                
            if data.startswith('/new_register '):

                user_nickname = data.strip('/new_register ')

                if not user_nickname in self.all_users_list:
                    if user_nickname != nickname:
                        self.all_users_list.append(user_nickname)
                        if add_new_contact_gui:
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

                        if my_contact_gui:
                            contacts_table.insert(parent = '', index = 'end',
                                    iid = self.my_contacts_list_and_dates.index(nickname_time),
                                    text = new_contact, values = replaced_time[:-3])
                        
                        self.insert_contacts_list(self.all_users_list)

                        message_box(f'{new_contact} added you to his/her contacts!', 'info')

            elif data.startswith('/recieve_message '):

                data = data.strip('/recieve_message ')
                if data != '':

                    messages = data.split('/separation/')
                    if chat_is_on:
                        text_widget.configure(state = 'normal')
                        for message in messages:
                            text_widget.insert(INSERT, f'{message} ({selected_contact})\n')
                        text_widget.configure(state = 'disabled')

            elif data.startswith('/recieve_last_five_messages '):

                if chat_is_on:

                    messages = data.strip('/recieve_last_five_messages ')
                    messages = messages.split('/separation/')

                    text_widget.configure(state = 'normal')

                    text_widget.insert(INSERT, f'The last five messages -\n')

                    for message in messages:
                        text_widget.insert(INSERT, f'{message}\n')

                    text_widget.insert(INSERT, f'new messages -\n')

                    text_widget.configure(state = 'disabled')

    def close_program(self):
        self.running = False
        self.client_socket.close()
        exit(0)

#my contacts screen

    def mycontacts_screen(self):
        global contacts_table, win, my_contact_gui

        win = CTk()
        win.geometry("750x420+585+330")
        win.title('Mychat')

        title = CTkLabel(win, text ='My Contacts', font = CTkFont(size = 30, weight = 'bold'))
        title.pack(pady = 10)

        table_style = ttk.Style()
        table_style.theme_use('clam')
        table_style.configure('Treeview',
                background = '#2A2D2E',
                foreground = 'white',
                fieldbackground = '#343638'
                )
        
        table_style.map('Treeview', background = [('selected', '#343638')])
        
        table_style.configure('Treeview.Heading',
                background = '#2A2D2E',
                foreground = colour_1,
                relief = 'flat'
        )

        table_style.map('Treeview.Heading', background = [('selected', '#343638')])
        
        table_style.configure('Treeview', highlightthickness = 0, bd = 0, font = (CTkFont, 11))
        table_style.configure('Treeview.Heading', font = (CTkFont, 13, 'bold'))
        table_style.layout('Treeview', [('Treeview.treearea', {'sticky': 'nswe'})])

        table_frame = CTkFrame(win, height = 400, width = 350, corner_radius = 26)
        table_frame.pack(pady = 15)

        contacts_table = ttk.Treeview(table_frame, style = 'Treeview')

        contacts_table['columns'] = ('Time-Added')

        contacts_table.column('#0')
        contacts_table.column('Time-Added')

        contacts_table.heading('#0', text = 'Contacts', anchor = W)
        contacts_table.heading('Time-Added', text = 'Time-Added', anchor = W)

        contacts_table.pack()

        add_contact_button = create_button(win, 'Add Contact', CTkFont, 30, 260, self.add_new_contact_screen, ())
        add_contact_button = add_contact_button.putinfo()
        add_contact_button.pack()

        log_out_button = create_button(win, 'Exit', CTkFont, 30, 260, self.logged_out, ())
        log_out_button = log_out_button.putinfo()
        log_out_button.pack(pady = 10)

        self.insert_my_contacts()

        contacts_table.bind('<Double-Button-1>', self.chat_screen)

        my_contact_gui = True

        win.mainloop()

    def insert_my_contacts(self):

        for contact in self.my_contacts_list_and_dates:
            data = contact.split()
            print(data)
            data[1] += '_'
            contacts_table.insert(parent = '', index = 'end', iid = self.my_contacts_list_and_dates.index(contact), text = data[0], values = data[1] + data[2][:-3])

    def logged_out(self):
        win.destroy()
        self.close_program()

#chat screen

    def chat_screen(self, e):
        global root, msg_entry, selected_contact, text_widget, chat_is_on

        selected_contact = ''
        selected_contact = contacts_table.focus()
        selected_contact = contacts_table.item(selected_contact)
        selected_contact = selected_contact.get('text')

        if selected_contact != '':
            if not chat_is_on:

                win.destroy()

                root = CTk()
                root.geometry("750x420+585+330")
                root.title(f'Mychat')

                # head label
                head_label = CTkLabel(root, text = f'Mychat - {selected_contact}', font = CTkFont(size = 30, weight = 'bold'))
                head_label.pack(pady = 10)

                # text widget
                text_widget = CTkTextbox(root, width=500, height=280, font = CTkFont(size = 12, weight = 'bold'), 
                                text_color = colour_1, corner_radius = 10, activate_scrollbars = True,
                                scrollbar_button_hover_color = colour_1, border_width = 4, border_color = colour_1,
                                border_spacing = 16, wrap = 'word')
                text_widget.pack(pady = 15)
                text_widget.configure(state = "disabled")

                # send button
                send_button = create_button(root, 'Send', CTkFont, 30, 260, self.send_message, ())
                send_button = send_button.putinfo()
                send_button.place(x = 400, y = 360)

                # message entry box
                msg_entry = CTkEntry(root, placeholder_text = 'Write a message..', width = 300, height = 44, text_color = colour_1, font = CTkFont(size = 16, weight = 'bold'))
                msg_entry.place(x = 60, y = 360)

                root.protocol('WM_DELETE_WINDOW', lambda: confirm_exit(root))

                chat_is_on = True

                self.client_socket.send(f'/recieve_last_five_messages {id} {selected_contact}'.encode('utf-8'))

                recieve_messages_thread = threading.Thread(target = self.recieve_message, args = (selected_contact,))
                recieve_messages_thread.start()

                root.mainloop()

    def send_message(self):
        
        if msg_entry.get() != '':

            now = datetime.now()
            now = now.strftime("%d/%m/%Y %H:%M")

            my_message = msg_entry.get()

            data = f'/new_message `{my_message}`{id}`{selected_contact}'
            self.client_socket.send(data.encode('utf-8'))

            text_widget.configure(state = 'normal')
            text_widget.insert(INSERT, f'{my_message} {now.split()[0]}_{now.split()[1]} (you)\n')
            msg_entry.delete('0', END)
            text_widget.configure(state = 'disabled')

    def recieve_message(self, selected_contact):

        while(chat_is_on):
            self.client_socket.send(f'/recieve_message `{id}`{selected_contact}'.encode('utf-8'))
            time.sleep(2)

#add new contact screen

    def add_new_contact_screen(self):
        global root, users_list, add_new_contact_gui, search_entry, my_contact_gui

        win.destroy()
        my_contact_gui = False

        root = CTk()
        root.geometry("750x420+585+330")
        root.title('Mychat')

        title_label = CTkLabel(root, text ='Add New Contact', font = CTkFont(size = 30, weight = 'bold'))
        title_label.pack(pady = 10)

        search_entry = CTkEntry(root, placeholder_text = 'Search for new contacts..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        search_entry.pack(pady = 10)

        users_list = Listbox(root, height = 8, width = 50, font = CTkFont(size = 14, weight = 'normal'),
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
        

        add_button = create_button(root, 'Add', CTkFont, 30, 260, self.add_new_contact_db, ())
        add_button = add_button.putinfo()
        add_button.pack(pady = 30)

        return_button = create_button(root, 'Return', CTkFont, 30, 260, self.return_to_my_contacts_screen, ())
        return_button = return_button.putinfo()
        return_button.pack(pady = 1)

        add_new_contact_gui = True

        self.insert_contacts_list(self.all_users_list)
        search_entry.bind("<KeyRelease>", self.create_contacts_list)

        root.mainloop()

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

            root.destroy()

            add_new_contact_gui = False

            message_box(f'{selected_contact} successfuly added!', 'info')

            self.mycontacts_screen()

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

        if add_new_contact_gui:

            users_list.delete('0', END)

            for contact in data:
                if not contact in self.my_contacts_nicknames_list:
                    if contact != nickname:
                        users_list.insert(END, contact)

    def return_to_my_contacts_screen(self):
        global add_new_contact_gui

        root.destroy()
        self.mycontacts_screen()
        add_new_contact_gui = False

#login

def login_screen(client_socket):
        global win, log_username_entry, log_password_entry

        win = CTk()
        print(type(win))
        win.geometry("750x420+585+330")
        win.title('Login page')
        win.iconbitmap('loginlockrefreshincircularbutton_80241.ico')

        set_default_color_theme('green')

        log_username_label = CTkLabel(win, text="Username", font = CTkFont(size = 30, weight = 'bold')).pack()
        log_username_entry = CTkEntry(win, placeholder_text = 'Enter username..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        log_username_entry.pack(pady = 10)

        log_password_label = CTkLabel(win, text="Password", font = CTkFont(size = 30, weight = 'bold')).pack()
        log_password_entry = CTkEntry(win, placeholder_text = 'Enter password..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        log_password_entry.configure(show = '*')
        log_password_entry.pack(pady = 10)

        checkbox = CTkCheckBox(win, text = "show password", fg_color = colour_1, 
                    checkbox_height = 20, checkbox_width = 20, corner_radius = 26, text_color = colour_1, command = show_password_login)
        checkbox.pack()

        login_frame = CTkFrame(win, width = 500, height = 200)
        login_frame.pack(pady=35)

        login_button = create_button(login_frame, 'Login', CTkFont, 30, 260, loged_in, client_socket)
        login_button = login_button.putinfo()
        login_button.pack()

        register_frame = CTkFrame(win, width = 500, height = 200)
        register_frame.pack(pady=4)

        register_button = create_button(register_frame, 'Register', CTkFont, 30, 260, register_screen, client_socket)
        register_button = register_button.putinfo()
        register_button.pack()

        win.mainloop()

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

#register

def register_screen(client_socket):
        global reg_nickname_entry, reg_username_entry, reg_passwordA_entry, reg_passwordB_entry, root

        win.destroy()

        root = CTk()
        root.geometry("750x420+585+330")
        root.title('Register Page')
        root.iconbitmap('loginlockrefreshincircularbutton_80241.ico')

        set_default_color_theme('green')

        reg_nickname_label = CTkLabel(root, text="Nickname", font = CTkFont(size = 20, weight = 'bold')).pack(pady = 10)
        reg_usename_label = CTkLabel(root, text="Username", font = CTkFont(size = 20, weight = 'bold')).pack(pady = 40)
        reg_password_label = CTkLabel(root, text="Password", font = CTkFont(size = 20, weight = 'bold')).pack(pady = 10)

        reg_nickname_entry = CTkEntry(root, placeholder_text = 'Enter nickname..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_nickname_entry.place(x = 220, y = 50)

        reg_username_entry = CTkEntry(root, placeholder_text = 'Enter username..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_username_entry.place(x = 220, y = 125)

        reg_passwordA_entry = CTkEntry(root, placeholder_text = 'Enter password..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_passwordA_entry.configure(show = '*')
        reg_passwordA_entry.place(x = 220, y = 200)

        reg_passwordB_entry = CTkEntry(root, placeholder_text = 'Confirm password..', width = 300, text_color = colour_1, font = CTkFont(size = 12, weight = 'bold'))
        reg_passwordB_entry.configure(show = '*')
        reg_passwordB_entry.place(x = 220, y = 235)

        checkbox = CTkCheckBox(root, text = "show password", fg_color = colour_1, 
                    checkbox_height = 20, checkbox_width = 20, corner_radius = 26, text_color = colour_1, command = show_password_register)
        checkbox.pack(pady = 68)

        submit_frame = CTkFrame(root, width = 500, height = 200)
        submit_frame.place(x = 240, y = 300)

        submit_button = create_button(submit_frame, 'Submit', CTkFont, 30, 260, submited, client_socket)
        submit_button = submit_button.putinfo()
        submit_button.pack()

        return_frame = CTkFrame(root, width = 500, height = 200)
        return_frame.place(x = 240, y = 360)

        return_button = create_button(return_frame, 'Return', CTkFont, 30, 260, return_to_login, client_socket)
        return_button = return_button.putinfo()
        return_button.pack()

        root.mainloop()

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
                    root.destroy()
                    win.destroy()
                else:
                    message_box('Your nickname is already taken', 'error')

            case False:
                message_box('Info must match', 'error')

def return_to_login(client_socket):
    root.destroy()
    login_screen(client_socket)



def confirm_exit(win):
    global chat_is_on

    answer = askyesno(title = 'Exit', message = 'Are you sure you want to exit ?')
    if answer:
        win.destroy()
        chat_is_on = False
        client_socket.mycontacts_screen()

def message_box(string, sign):
    msg = create_message(sign, string)
    msg.show()

client_socket = create_client(HOST, PORT)
