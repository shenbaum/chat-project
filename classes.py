from customtkinter import *
from tkinter import messagebox

#button class

class create_button(): 
    def __init__(self, surface, text, font, size, width, command, var):
        self.surface = surface
        self.text = text
        self.font = font
        self.size = size
        self.width = width
        self.command = command
        self.var = var

    def putinfo(self):
        if self.var == ():
            button = CTkButton(self.surface, text = self.text, font = self.font(size = self.size, weight = 'bold'), 
                               width = self.width, command = self.command)
            
        else:
            button = CTkButton(self.surface, text = self.text, font = self.font(size = self.size, weight = 'bold'), 
                               width = self.width, command = lambda: self.command(self.var))
            
        return button
    
#info\error window class

class create_message():
    def __init__(self, sign, string):
        self.sign = sign
        self.string = string

    def show(self):
        return messagebox.showinfo(self.sign, self.string)
