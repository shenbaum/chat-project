import socket
import threading
from tkinter import ttk
from tkinter import *
from datetime import datetime
import tkinter.scrolledtext

HOST, PORT = '192.168.1.41', 4242

hostname = socket.gethostname()
my_ip_address = socket.gethostbyname(hostname)

username = input('choose your usename: ')

now = datetime.now()

column = 0

chat_gui = False

class create_socket():

    def __init__(self, HOST, PORT):

        self.client_socket = socket.socket()
        self.client_socket.connect((HOST, PORT))
        self.running = True

        self.receive_thread = threading.Thread(target = self.receive)

        self.receive_thread.start()

    def write(self):
            
         if chat_gui:
            message = message_entry.get()
            data = f'{message},{username},{my_ip_address}'
            self.client_socket.send(data.encode('utf-8'))

    def receive(self):
        global column

        while(self.running):

            data = self.client_socket.recv(1024).decode()
            details = data.split(',')
            if details[0] != '':
                insert(column, details[0], details[1], details[2])
                message_entry.delete(0, END)

    def stop(self):
        self.running = False
        self.client_socket.close()
        exit(0)

    def close_server(self):
        self.client_socket.close()

def main_screen():
    global message_entry, table, chat_gui

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
                         text = 'Send', font = ('Arial', 12, 'bold'), command = client_socket.write)
    send_button.place(x = 266, y = 310)

    table = ttk.Treeview(win)
    table['columns'] = ('Username', 'IP', 'Time')

    table.column('#0', width = 360)
    table.column('Username', anchor = W, width = 100)
    table.column('IP', anchor = CENTER, width = 100)
    table.column('Time', anchor = W, width = 45)

    table.heading('#0', text = 'Message', anchor = W)
    table.heading('Username', text = 'Username', anchor = W)
    table.heading('IP', text = 'IP', anchor = CENTER)
    table.heading('Time', text = 'Time', anchor = W)

    table.pack()

    scrollbar = Scrollbar(win)
    scrollbar.pack(side = RIGHT, fill = Y)

    chat_gui = True

    win.mainloop()

def insert(index, message, nickname, ip):
    global column, table

    if nickname == username:
        nickname = nickname + ' (you)'

    if message != '':
        table.insert(parent = '', index = 'end', iid = index,
            text = message, values = (nickname, ip, now.strftime('%H : %M')))
        
    column += 1

chat_screen_thread = threading.Thread(target = main_screen)
chat_screen_thread.start()

client_socket = create_socket(HOST, PORT)
