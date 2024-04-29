from tkinter import *
from tkinter import messagebox
import threading
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
from client import *

#colours
colour_1 = '#020f12'
colour_2 = '#05d7ff'
colour_3 = '#65e7ff'
colour_4 = 'BLACK'

with open('mykey.key', 'rb') as mykey:
    key = mykey.read()
            
f = Fernet(key)

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

def loged_in():

    check = False
    username, password = GetLoginInfo()

    f = Fernet(key)

    with open('enc_info.csv', 'rb') as file:
        lines = file.readlines()
        for line in lines:
            decrypted_info = f.decrypt(line).decode('ASCII')
            decrypted_info = decrypted_info.split()
            if username == decrypted_info[0] and password == decrypted_info[1]:
                check = True
                break

        match check:
            case True:
                message('You have been Connected successfully!', 'info')
                win.destroy()
                socket_procces()
            case False:
                message('Invalid username or password', 'error')

def message(string, sign):
    match sign:
        case 'info':
            msg = messagebox.showinfo('info', string)
        case 'error':
            msg = messagebox.showerror('Error', string)

def GetLoginInfo():
    log_username = log_username_entry.get()
    log_password = log_password_entry.get()

    log_username_entry.delete(0, 'end')
    log_password_entry.delete(0, 'end')

    return log_username, log_password

def get_register_info():
    reg_username = reg_username_entry.get()
    reg_passwordA = reg_passwordA_entry.get()
    reg_passwordB = reg_passwordB_entry.get()
    return reg_username, reg_passwordA, reg_passwordB

def check_info():
    if get_register_info()[1] == get_register_info()[2]:
        if get_register_info()[0] != "":
            return True
    return False

def submited():

    check = check_info()
    match check:
        case True:

            info = bytes(f"{get_register_info()[0]} {get_register_info()[1]}", "utf-8")
            encrypted_info = f.encrypt(info)

            with open('enc_info.csv', 'ab') as file:
                file.write(encrypted_info)
                file.close()

            with open('enc_info.csv', 'a') as file:
                file.write("\n")

            win.destroy()
            return message('You have been registered successfully!', 'info')

        case False:
            return message('Info must match', 'error')

def show_password_login():
    if log_password_entry.cget('show') == '*':
        log_password_entry.config(show = '')
    else: log_password_entry.config(show = '*')

def show_password_register():
    if reg_passwordA_entry.cget('show') == '*':
        reg_passwordA_entry.config(show = '')
        reg_passwordB_entry.config(show = '')
    else:
        reg_passwordA_entry.config(show = '*')
        reg_passwordB_entry.config(show = '*')

def main_screen():
    global log_username_entry, log_password_entry, win

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
                foreground = colour_2, activebackground = colour_1, activeforeground = colour_2, command = show_password_login)
    checkbox.pack()

    login_frame = Frame(win, highlightbackground = colour_2, highlightthickness = 2, bd = 0)
    login_frame.place(x = 128, y = 115)

    login_button = create_button(login_frame, colour_1, colour_2, colour_2, colour_1, 2, colour_2, 
                        'white', 13, 1, 0, 'hand1', "Connect", ('Arial', 12, 'bold'), loged_in)
    login_button = login_button.putinfo()
    login_button.pack()

    register_frame = Frame(win, highlightbackground = colour_2, highlightthickness = 2, bd = 0)
    register_frame.place(x = 128, y = 160)

    register_button = create_button(register_frame, colour_1, colour_2, colour_2, colour_1, 2, colour_2, 
                        'white', 13, 1, 0, 'hand1', "Register", ('Arial', 12, 'bold'), register_screen)
    register_button = register_button.putinfo()
    register_button.pack()

    win.mainloop()

def register_screen():
    global reg_username_entry, reg_passwordA_entry, reg_passwordB_entry, win

    win = Tk()
    win.geometry("400x200")
    win.title('Register Page')
    win.configure(bg = colour_1)
    win.iconbitmap('loginlockrefreshincircularbutton_80241.ico')

    reg_usename_label = Label(win, text="Username", font = 'Arial', bg = colour_1, fg = colour_2).place(x=70, y=27)
    reg_password_label = Label(win, text="Password", font = 'Arial', bg = colour_1, fg = colour_2).place(x=70, y=57)

    reg_username_entry = Entry(win)
    reg_username_entry.place(x=180, y=30)

    reg_passwordA_entry = Entry(win, show = '*')
    reg_passwordA_entry.place(x=180, y=60)

    reg_passwordB_entry = Entry(win, show = '*')
    reg_passwordB_entry.place(x=180, y=90)

    checkbox = Checkbutton(win, text = "show password", background = colour_1, 
                foreground = colour_2, activebackground = colour_1, activeforeground = colour_2, command = show_password_register)
    checkbox.place(x=180, y= 110)

    submit_frame = Frame(win, highlightbackground = colour_2, highlightthickness = 2, bd = 0)
    submit_frame.place(x = 170, y = 140)

    submit_button = create_button(submit_frame, colour_1, colour_2, colour_2, colour_1, 2, colour_2, 'white', 13, 1, 0, 'hand1', "Submit", ('Arial', 12, 'bold'), submited)
    submit_button = submit_button.putinfo()
    submit_button.pack()

    win.mainloop()

main_screen()
