import socket
import threading
from tkinter import ttk
from tkinter import *
from datetime import datetime
import tkinter.scrolledtext
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from tkinter import messagebox

HOST, PORT = '192.168.1.216', 8820

#colours
colour_1 = '#020f12'
colour_2 = '#05d7ff'
colour_3 = '#65e7ff'
colour_4 = 'BLACK'

with open('mykey.key', 'rb') as mykey:
    key = mykey.read()

f = Fernet(key)

hostname = socket.gethostname()
my_ip_address = socket.gethostbyname(hostname)

column = 0

chat_gui = False

nickname = ''
nicknames = []

check = 'false'

class create_socket():

    def __init__(self, HOST, PORT):

        self.client_socket = socket.socket()
        self.client_socket.connect((HOST, PORT))
        self.running = True
        self.nickname = ''

        self.choose_nickname()
        self.nickname = nickname

        self.login_screen()

        if check == 'false':
            self.close_program()

        else:

            self.receive_thread = threading.Thread(target = self.receive)
            self.main_screen_thread = threading.Thread(target = self.main_screen)

            self.receive_thread.start()
            self.main_screen_thread.start()

    def write(self):
            
         if chat_gui:
            message = message_entry.get()
            data = f'{message}^{self.nickname}^{my_ip_address}'
            self.client_socket.send(data.encode('utf-8'))
            message_entry.delete(0, END)

    def receive(self):
        global column

        while(self.running):

            data = self.client_socket.recv(1024).decode()
            if '^' in data:
                details = data.split('^')
                if details[0] != '':
                    if len(details) == 3:
                        self.insert(column, details[0], details[1], 'Everyone', details[2])

                    elif len(details) == 4:
                        if details[3] == my_ip_address:
                            self.insert(column, f'{details[1]}', 'Me', details[0], details[3])
                        else:
                            self.insert(column, f'{details[1]}', details[2], 'Me', details[3])

    def close_program(self):
        self.running = False
        self.client_socket.close()
        exit(0)

#chat

    def main_screen(self):
        global message_entry, table, chat_gui, nickname_list

        win = Tk()
        win.geometry('700x400')
        win.title('chat')

        colour_1 = 'white'
        colour_2 = 'grey'

        title = Label(win, text ='chat', font = "50")  
        title.pack()

        message_entry = Entry(win, width = 67, font = ('Arial 13'))
        message_entry.place(x = 39, y = 270)

        send_button = Button(win, background = colour_1, foreground = colour_2, activebackground = colour_2,
                            activeforeground = colour_1, highlightthickness = 2, highlightbackground = colour_2,
                            highlightcolor = 'white', width = 13, height = 1, border = 0, cursor = 'hand1',
                            text = 'Send', font = ('Arial', 12, 'bold'), command = self.write)
        send_button.place(x = 266, y = 310)

        table = ttk.Treeview(win)
        table['columns'] = ('Sender', 'Reciever', 'IP', 'Time')

        table.column('#0', width = 360)
        table.column('Sender', anchor = W, width = 100)
        table.column('Reciever', anchor = W, width = 100)
        table.column('IP', anchor = CENTER, width = 95)
        table.column('Time', anchor = W, width = 45)

        table.heading('#0', text = 'Message', anchor = W)
        table.heading('Sender', text = 'Sender', anchor = W)
        table.heading('Reciever', text = 'Reciever', anchor = W)
        table.heading('IP', text = 'IP', anchor = CENTER)
        table.heading('Time', text = 'Time', anchor = W)

        table.pack()

        nickname_list = Listbox(win, height = 5, width = 30)
        nickname_list.place(x = 39, y = 300)

        chat_gui = True

        win.mainloop()

    def insert(self, index, message, sender, reciever, ip):
        global column, table

        now = datetime.now()

        if sender == self.nickname:
            sender = 'Me'

        if message != '':
            table.insert(parent = '', index = 'end', iid = index,
                text = message, values = (sender, reciever, ip, now.strftime('%H : %M')))
            
        column += 1

#nickname screen

    def choose_nickname(self):
        global nickname_entry, win

        win = Tk()
        win.geometry("200x100")
        win.title('Choose nickname page')
        win.configure(background = colour_1)
        win.iconbitmap('loginlockrefreshincircularbutton_80241.ico')

        nickname_label = Label(win, text="Nickname", font = 'Arial', bg = colour_1, fg = colour_2).pack()
        nickname_entry = Entry(win)
        nickname_entry.pack()

        nickname_frame = Frame(win, highlightbackground = colour_2, highlightthickness = 2, bd = 0)
        nickname_frame.place(x = 35, y = 50)

        login_button = create_button(nickname_frame, colour_1, colour_2, colour_2, colour_1, 2, colour_2, 
                            'white', 13, 1, 0, 'hand1', "Choose", ('Arial', 11, 'bold'), self.return_nickname)
        login_button = login_button.putinfo()
        login_button.pack()

        win.mainloop()

    def return_nickname(self):
        global nickname

        if nickname_entry.get() != '':
            nickname = nickname_entry.get()
            self.client_socket.send(nickname.encode('utf-8'))
            win.destroy()
        else:
            self.message('Incorrect input', 'error')

#login

    def login_screen(self):
        global win, log_username_entry, log_password_entry

        win = Tk()
        win.geometry("400x200")
        win.title('Login page')
        win.configure(background = colour_1)
        win.iconbitmap('loginlockrefreshincircularbutton_80241.ico')

        log_username_label = Label(win, text="Username", font = 'Arial', bg = colour_1, fg = colour_2).pack()
        log_username_entry = Entry(win)
        log_username_entry.pack()

        log_password_label = Label(win, text="Password", font = 'Arial', bg = colour_1, fg = colour_2).pack()
        log_password_entry = Entry(win, show = '*')
        log_password_entry.pack()

        checkbox = Checkbutton(win, text = "show password", background = colour_1, 
                    foreground = colour_2, activebackground = colour_1, activeforeground = colour_2, command = self.show_password_login)
        checkbox.pack()

        login_frame = Frame(win, highlightbackground = colour_2, highlightthickness = 2, bd = 0)
        login_frame.place(x = 128, y = 115)

        login_button = create_button(login_frame, colour_1, colour_2, colour_2, colour_1, 2, colour_2, 
                            'white', 13, 1, 0, 'hand1', "Connect", ('Arial', 12, 'bold'), self.loged_in)
        login_button = login_button.putinfo()
        login_button.pack()

        register_frame = Frame(win, highlightbackground = colour_2, highlightthickness = 2, bd = 0)
        register_frame.place(x = 128, y = 160)

        register_button = create_button(register_frame, colour_1, colour_2, colour_2, colour_1, 2, colour_2, 
                            'white', 13, 1, 0, 'hand1', "Register", ('Arial', 12, 'bold'), self.register_screen)
        register_button = register_button.putinfo()
        register_button.pack()

        win.mainloop()

    def show_password_login(self):
        if log_password_entry.cget('show') == '*':
            log_password_entry.config(show = '')
        else: 
            log_password_entry.config(show = '*')

    def GetLoginInfo(self):
        log_username = log_username_entry.get()
        log_password = log_password_entry.get()

        log_username_entry.delete(0, 'end')
        log_password_entry.delete(0, 'end')

        return log_username, log_password

    def loged_in(self):
        global check

        username, password = self.GetLoginInfo()
        if username != '' and password != '':

            info = bytes(f'{username} {password}', 'utf8')
            encrypted_info = f.encrypt(info)
            
            self.client_socket.send('logged-in '.encode('utf-8') + encrypted_info)

            check = self.client_socket.recv(1024).decode()

        match check:
            case 'true':
                self.message('You have been Connected successfully!', 'info')
                win.destroy()

            case 'false':
                self.message('Invalid username or password', 'error')

#register

    def register_screen(self):
        global reg_username_entry, reg_passwordA_entry, reg_passwordB_entry, root

        root = Tk()
        root.geometry("400x200")
        root.title('Register Page')
        root.configure(bg = colour_1)
        root.iconbitmap('loginlockrefreshincircularbutton_80241.ico')

        reg_usename_label = Label(root, text="Username", font = 'Arial', bg = colour_1, fg = colour_2).place(x=70, y=27)
        reg_password_label = Label(root, text="Password", font = 'Arial', bg = colour_1, fg = colour_2).place(x=70, y=57)

        reg_username_entry = Entry(root)
        reg_username_entry.place(x=180, y=30)

        reg_passwordA_entry = Entry(root, show = '*')
        reg_passwordA_entry.place(x=180, y=60)

        reg_passwordB_entry = Entry(root, show = '*')
        reg_passwordB_entry.place(x=180, y=90)

        checkbox = Checkbutton(root, text = "show password", background = colour_1, 
                    foreground = colour_2, activebackground = colour_1, activeforeground = colour_2, command = self.show_password_register)
        checkbox.place(x=180, y= 110)

        submit_frame = Frame(root, highlightbackground = colour_2, highlightthickness = 2, bd = 0)
        submit_frame.place(x = 170, y = 140)

        submit_button = create_button(submit_frame, colour_1, colour_2, colour_2, colour_1, 2, colour_2, 'white', 13, 1, 0, 'hand1', "Submit", ('Arial', 12, 'bold'), self.submited)
        submit_button = submit_button.putinfo()
        submit_button.pack()

        win.mainloop()

    def get_register_info(self):
        reg_username = reg_username_entry.get()
        reg_passwordA = reg_passwordA_entry.get()
        reg_passwordB = reg_passwordB_entry.get()
        return reg_username, reg_passwordA, reg_passwordB

    def show_password_register(self):
        if reg_passwordA_entry.cget('show') == '*':
            reg_passwordA_entry.config(show = '')
            reg_passwordB_entry.config(show = '')
        else:
            reg_passwordA_entry.config(show = '*')
            reg_passwordB_entry.config(show = '*')

    def submited(self):

        check = False
        if self.get_register_info()[1] == self.get_register_info()[2]:
            if self.get_register_info()[1] != '':
                if self.get_register_info()[0] != '':
                    check = True

        match check:
            case True:

                info = bytes(f"{self.get_register_info()[0]} {self.get_register_info()[1]}", "utf-8")
                encrypted_info = f.encrypt(info)

                self.client_socket.send('registered '.encode('utf-8') + encrypted_info)

                root.destroy()
                return self.message('You have been registered successfully!', 'info')

            case False:
                return self.message('Info must match', 'error')

#message

    def message(self, string, sign):
        msg = create_message(sign, string)
        msg.show()

class create_button():
    def __init__(self, surface, background, foreground, activebackground, activeforeground, highlightthickness, 
                highlightbackground, highlightcolor, width, height, border, cursor, text, font, command):
        self.surface = surface
        self.background = background
        self.foreground = foreground
        self.activebackground = activebackground
        self.activeforeground = activeforeground
        self.highlightthickness = highlightthickness
        self.highlightbackground = highlightbackground
        self.highlightcolor = highlightcolor
        self.width = width
        self.height = height
        self.border = border
        self.cursor = cursor
        self.text = text
        self.font = font
        self.command = command

    def putinfo(self):
        button = Button(self.surface, background=self.background, foreground=self.foreground, activebackground=self.activebackground, 
                        activeforeground=self.activeforeground, highlightthickness=self.highlightthickness, highlightbackground=self.highlightbackground, 
                        highlightcolor=self.highlightcolor, width=self.width, height=self.height, border=self.border, cursor=self.cursor, 
                        text=self.text, font=self.font, command = self.command)
        return button

class create_message():
    def __init__(self, sign, string):
        self.sign = sign
        self.string = string

    def show(self):
        return messagebox.showinfo(self.sign, self.string)

client_socket = create_socket(HOST, PORT)
