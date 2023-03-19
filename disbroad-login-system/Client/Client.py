from logging import basicConfig, DEBUG, CRITICAL, FileHandler, StreamHandler, info, error, debug
import socket
import threading
import tkinter as tk
from sys import stdout
from tkinter import scrolledtext
from tkinter import messagebox
from os import getcwd, mkdir
from datetime import datetime

directory = f'{getcwd()}'
debug(f"Current directory: {directory}")

dt = datetime.now().strftime("%d.%m.%Y")
debug(f"Current date: {dt}")
try:
    basicConfig(
        level=DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s',
        handlers=[
            FileHandler(f'{directory}/Debug_Logs/Client_Debug_{dt}.txt'),
            StreamHandler(stdout)
        ]
    )
    info("basicConfig ran successfully")
except FileNotFoundError:
    error("Debug Logs folder not found, creating one now")
    mkdir(f'{directory}/Debug_Logs')
    info("Debug Logs folder created")
    basicConfig(
        level=DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s',
        handlers=[
            FileHandler(f'{directory}/Debug_Logs/Client_Debug_{dt}.txt'),
            StreamHandler(stdout)
        ]
    )
    info("basicConfig ran successfully")

info('\n\n App is starting\n\n')

HOST = ''
PORT = 0
configtxt = f'{directory}\\config.txt'


def get_config():
    try:
        # Condensed the reading to make it more readable
        with open(configtxt, "r") as config:
            for line in config.readlines():
                if line.startswith('server_ip:'):
                    ip = line.split(': ')[1]
                    host = ip.split('\n')[0]
                elif line.startswith('server_port:'):
                    port = int(line.split(': ')[1])
        debug(f'Grabbed config data from {configtxt}')
    except FileNotFoundError:
        error(f'Config file not found at {configtxt}')
        exit("Config file not found")

    return host, port  # Returning the variables makes it way more readable, additionally, globals are not super
    # optimised and can cause mem leaks


DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'
WHITE = "white"
FONT = ("Helvetica", 17)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)
app_version = 'Disbroad V0.1.2'
commands = ['/help', '/updates', '/settings']
typing = False
users_typing = []

debug('Set UI variables')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
debug('Created client socket')


def add_message(message):
    print(f'Message: {message}')
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)
    message_box.yview_moveto(message_box.yview()[1])
debug('Defined the add_message function')


def connection_check(client):
    try:
        client.send(b'')
        return True
    except WindowsError as err:
        if err.winerror == 10038 or err.winerror == 10057:
            info('Connection test failed')
            return False
        else:
            error(f'Connection test failed, unknown error {err}')
            return False


def close_window():
    connected = connection_check(client)
    if connected:
        debug('Closing the connection')
        client.sendall(b'Close Connection')
        debug('Closing the Window\n')
        root.destroy()
    else:
        debug('Closing the Window\n')
        root.destroy()
debug('Defined the close_window function')


def connect():
    debug('Attempting to connect to the server')
    HOST, PORT = get_config()
    try:
        client.connect((HOST, PORT))
        add_message('INFO | Successfully connected to the server')
        debug(f'Connected to {HOST}:{PORT}')
    except Exception as err:
        error(f'Unable to connect to the server on {HOST}:{PORT} with error:\n {err}')
        messagebox.showerror('Connection Error', f'Failed to connect to server {HOST}:{PORT}')
    username = f'USERNAME | {username_textbox.get()}'
    if username != 'USERNAME | ':
        debug('Username is not empty, attempting to send to server')
        client.sendall(username.encode())
    else:
        messagebox.showerror('Invalid username', 'Username cannot be empty')
    threading.Thread(target=listen_for_messages_from_server, args=(client,)).start()
debug('Defined the connect function')


def send_message(message):
    if message != '':
        if message == commands[1]:
            updates = tk.Tk()
            updates.geometry('300x300')
            tk.Label(updates, text=f'{app_version.upper()} UPDATES', bg=DARK_GREY, fg=WHITE).grid(column=0, row=0)
            tk.Label(updates, text='1. Added the Update Log', bg=DARK_GREY, fg=WHITE).grid(column=0, row=1)
            tk.Label(updates, text='2. Implemented /commands', bg=DARK_GREY, fg=WHITE).grid(column=0, row=2)
            tk.Label(updates, text='3. General bug fixes', bg=DARK_GREY, fg=WHITE).grid(column=0, row=3)
            tk.Label(updates, text='4. App optimizations', bg=DARK_GREY, fg=WHITE).grid(column=0, row=4)
        elif message == commands[0]:
            msg = 'All of the Current Commands:\n'
            for cmd in commands:
                msg += f'{cmd}\n'
            add_message(msg)
        else:
            info(f'Message: {message}')
            debug('Message is not empty, attempting to send to server')
            client.sendall(message.encode())
            debug('Clearing the text input')
            message_textbox.delete(0, len(message))
    else:
        info('Message input is empty')


debug('Defined the send_message function')


def enter_pressed(event):
    send_message(message_textbox.get())


def key_pressed(event):
    global typing
    try:
        if message_textbox.get() != '':
            if not typing:
                typing = True
                send_message('!?UserIStyping?!')
        else:
            typing = False
            send_message('!?UserISnotTYPING?!')
    except WindowsError as err:
        if err.winerror == 10057:
            info('Client was not connected to the server when trying to send a typing message')
        else:
            error(f'Unknown error when trying to send a typing message: {err}')


debug('Defined the enter_pressed function')


root = tk.Tk()
root.geometry("600x620")
root.title(f'{app_version} Closed Beta')
root.resizable(False, False)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

root.protocol("WM_DELETE_WINDOW", close_window)
root.bind('<Return>', enter_pressed)
root.bind('<Key>', key_pressed)

top_frame = tk.Frame(root, width=600, height=100, bg=DARK_GREY)
top_frame.grid(row=0, column=0, sticky=tk.NSEW)

middle_frame = tk.Frame(root, width=600, height=400, bg=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky=tk.NSEW)

bottom_frame = tk.Frame(root, width=600, height=100, bg=MEDIUM_GREY)
bottom_frame.grid(row=2, column=0, sticky=tk.NSEW)

username_label = tk.Label(top_frame, text="Enter username:", font=FONT, bg=DARK_GREY, fg=WHITE)
username_label.pack(side=tk.LEFT, padx=10)

username_textbox = tk.Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=23)
username_textbox.pack(side=tk.LEFT)

username_button = tk.Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=connect)
username_button.pack(side=tk.LEFT, padx=15)

message_textbox = tk.Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=38)
# message_textbox.pack(side=tk.LEFT, padx=10)
message_textbox.grid(column=0, row=0)

# message_button = tk.Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=send_message)
# message_button.pack(side=tk.LEFT, padx=10)
# message_button.grid(column=1, row=0)

message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE, width=67, height=26.5)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP)

typing_label = tk.Label(bottom_frame, font=FONT, bg=MEDIUM_GREY)
typing_label.grid(column=0, row=1)


debug('Created the UI and awaiting root.mainloop to be called')


def listen_for_messages_from_server(user):
    global client
    while 1:
        message = user.recv(2048).decode('utf-8')
        if message != '':
            debug(f'Message received: {message}')
            if message.endswith('has joined the Chat Room'):
                add_message(message)
            elif message.startswith('MESSAGE | '):
                username = message.split(" | ")[1]
                content = message.split(' | ')[2]
                add_message(f"[{username}] {content}")
            elif message == 'Close Connection':
                client.close()
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif message.startswith('Online Users | '):
                add_message(message)
            elif message == 'USERNAME MATCH':
                messagebox.showerror('Username Error', 'Another User has already taken this username')
                client.close()
            elif message == 'USERNAME UNIQUE':
                username_textbox.config(state=tk.DISABLED)
                username_button.config(state=tk.DISABLED)
            elif message.startswith('TYPING | '):
                username = message.split(' | ')[1]
                users_typing.append(username)
                typ_len = len(users_typing)
                if typ_len > 1:
                    typing_label.config(text='Multiple people are typing')
                else:
                    typing_label.config(text=f'{username} is Typing')
            elif message.startswith('NOTTYPING | '):
                typing_label.config(text='')

        else:
            messagebox.showerror("Error", "Message received from client is empty")


debug('Defined the listen_for_messages_from_server function')

if __name__ == '__main__':
    debug('Running mainloop')
    root.mainloop()
