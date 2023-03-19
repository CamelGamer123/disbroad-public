from logging import basicConfig, DEBUG, FileHandler, StreamHandler, info, error, debug, warning
from socket import gethostbyname, gethostname, socket, AF_INET, SOCK_STREAM
from threading import Thread
from sys import stdout
from tkinter import scrolledtext, messagebox, Frame, Tk, NORMAL, END, DISABLED, Label, Entry, Button, LEFT, NSEW, TOP, \
    PhotoImage
from os import getcwd, mkdir, path, remove, listdir, system
from datetime import datetime
from time import time
from json import load, JSONDecodeError, dump, decoder, loads
from exceptions import *


directory = f'{getcwd()}'
dt = datetime.now().strftime("%d.%m.%Y")

defaultConfig = {
    "server_ip": "auto",
    "server_port": 81,
    "version": "0.1.4",
    "log_max_age": 24,
    "contentFilter": False,
    "contentFilterReplace": "*"
}

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
except FileNotFoundError:  # Handles events where the logs folder is not found
    mkdir(f'{directory}/Debug_Logs')  # Creates a debug_logs folder
    basicConfig(  # Tries to run the basicConfig again
        level=DEBUG,
        format='%(asctime)s:%(levelname)s:%(message)s',
        handlers=[
            FileHandler(f'{directory}/Debug_Logs/Client_Debug_{dt}.txt'),
            StreamHandler(stdout)
        ]
    )
    error("Debug Logs folder was not found, one was created")
    info("basicConfig ran successfully\n\n")
    debug('Starting Core\n\n')


configtxt = f'{directory}\\config.txt'


class Config:
    """
    Stores the config data from the config file and provides a refresh method to update the data dynamically. This is
    useful for when the config file is changed while the program is running.
    """

    def __init__(self):
        info('Initializing Config object')
        self.ip = None
        self.host = None
        self.port = None
        self.version = None
        self.log_max_age = None
        self.contentFilter = False
        self.contentFilterReplace = "*"

        self.refresh()

    def write(self, data):
        """
        Writes the data to the config file
        :param data: The data to write to the config file
        """
        with open(f'{directory}\\config.json', 'w') as self.config:
            dump(data, self.config, indent=4)
        info(f'Wrote config data to {directory}\\config.json')

    @staticmethod
    def rewrite():
        """
        Writes the default config data to the config file
        """
        with open(f'{directory}\\config.json', 'w') as config:
            dump(defaultConfig, config, indent=4)
        info(f'Wrote default config data to {directory}\\config.json')

    def refresh(self):
        # Tries to grab the config data from the config file
        try:
            with open(f'{directory}\\config.json', 'r') as config:
                data = load(config)
            info(f'Grabbed config data from {directory}\\config.json')

        except FileNotFoundError:  # If the config file is not found, it will create one with the default values
            with open(f'{directory}\\config.json', 'w') as config:
                self.rewrite()
            info(f'Created config file at {directory}\\config.json')
            self.refresh()
            return

        except decoder.JSONDecodeError:  # If the config file is corrupted, it will create a new one with the default
            # values
            with open(f'{directory}\\config.json', 'w') as config:
                self.rewrite()
            info(f'Config file was corrupted, default config data was written to {directory}\\config.json')
            self.refresh()
            return

        try:
            with open(f'{directory}\\bannedWords.json', 'r') as bannedWords:
                words = load(bannedWords)
            info(f'Grabbed banned words from {directory}\\bannedWords.json')

        except FileNotFoundError:
            with open(f'{directory}\\bannedWords.json', 'w') as bannedWords:
                # Need to implement a rewrite for the banned words file
                pass
            info(f'Created banned words file at {directory}\\bannedWords.json')
            self.refresh()
            return

        if data["server_ip"] == "auto":
            warning("-" * 10 + "WARNING: IP SET TO auto THIS IS ONLY FOR TESTING" + "-" * 10)
            self.ip = gethostbyname(gethostname())
        else:
            self.ip = data['server_ip']
        self.host = self.ip
        self.port = data['server_port']
        self.version = data['version']
        self.log_max_age = int(data['log_max_age'])
        self.contentFilter = data['contentFilter']
        self.contentFilterReplace = data['contentFilterReplace']

        info(f"Config data: "
             f"Host: {self.host}, Port: {self.port}, Version: {self.version}, Log Max Age: {self.log_max_age},"
             f" Content Filter: {self.contentFilter}, Content Filter Replace: {self.contentFilterReplace}")


config = Config()
# This gets the current version of the client from the config file and discard the rest of the data
version = config.version

info('Defined the get_config function')

DARK_GREY = '#121212'
MEDIUM_GREY = '#1F1B24'
OCEAN_BLUE = '#464EB8'
WHITE = "white"
FONT = ("Helvetica", 17)
BUTTON_FONT = ("Helvetica", 15)
SMALL_FONT = ("Helvetica", 13)
app_version = f'Disbroad V{version}'
commands = ['/help', '/settings', '/users', '/users typing', '/updates']
typing = False
users_typing = []
info('Set UI variables')

client = socket(AF_INET, SOCK_STREAM)
info('Created client socket')


def file_age(filepath):
    try:
        return time() - path.getmtime(filepath)
    except FileNotFoundError:
        return 0


def delete_old_logs():
    """
    Deletes log files that are older than the user's specified log retention time.
    """
    # Gets the user's specified log retention time
    config.refresh()
    max_age = config.log_max_age * 3600
    for log_file in listdir(f'{directory}/Debug_Logs'):
        if file_age(log_file) > int(max_age):
            remove(log_file)
            info(f'Deleted log file {log_file}')


def check_message_for_letters(message):
    """
    Checks if a message contains any letters
    :param message: The message to check
    :return: True if the message contains letters, False if it does not
    """
    for letter in message:
        if letter.isalnum():
            return True
    return False


def add_message(message):
    """
    Adds a message to the message box on the gui
    """
    debug(f'Adding message: {message}')
    message_box.config(state=NORMAL)
    message_box.insert(END, message + '\n')
    message_box.config(state=DISABLED)
    message_box.yview_moveto(message_box.yview()[1])


info('Defined the add_message function')


def connection_check(client):
    try:
        client.send(b'')
        return True
    except WindowsError as err:
        if err.winerror == 10038 or err.winerror == 10057:
            info('Connection test failed')
        else:
            warning(f'Connection test failed, unknown error {err}')
        return False


def close_window():
    connected = connection_check(client)
    if connected:
        if typing:
            send_message('!?UserISnotTYPING?!')
        debug('Telling server to close connection')
        send_message('Close Connection')
        debug('Closing the Window\n')
        root.destroy()
        debug('Shutting down core')
    else:
        debug('Closing the Window\n')
        root.destroy()
        debug('Shutting down core')


debug('Defined the close_window function')


def set_config(setting, value):  # This needs to be moved into the config class
    """
    Sets the value of a setting in the config file
    """
    with open(f'{directory}\\config.json', 'r') as config_file:
        data = load(config_file)
    data[setting] = value
    with open(f'{directory}\\config.json', 'w') as config_file:
        dump(data, config_file, indent=4)
    info(f'Set {setting} to {value}')


def show_changelog():
    # Create and configure the changelog window
    updates = Tk()
    updates.geometry('400x400')
    updates.title(f'{app_version.upper()} UPDATES')
    updates.configure(bg=DARK_GREY)
    updates.resizable(False, False)

    Label(updates, text=f'{app_version.upper()} UPDATES', bg=DARK_GREY, fg=WHITE).pack(padx=10, pady=10, side=TOP,
                                                                                       anchor="nw")

    updates_string = ''
    with open(f'{directory}/updates.txt', 'r') as updates_file:
        for line in updates_file:
            updates_string += line

    Label(updates, text=updates_string, bg=DARK_GREY, fg=WHITE).pack(padx=10, pady=10, side=TOP, anchor="w")


def handle_command(command: str):  # This is extremely poorly made and should be rewritten once the new comms system and
    # GUI overhaul is implemented
    """
    Handles the commands that the user types into the message box
    """

    """
    Old Commands Code for Reference:
    # if message.lower() in commands:
        #     # If the message is part of the commands list
        #     if message.lower() == commands[1]:  # updates
        #         updates = tk.Tk()
        #         updates.geometry('350x300')
        #         updates.title(f'{app_version.upper()} UPDATES')
        #         tk.Label(updates, text=f'{app_version.upper()} UPDATES', bg=DARK_GREY, fg=WHITE).grid(column=0, row=0)
        #         tk.Label(updates, text='1. Added the Update Log\n'
        #                                '2. Implemented /help\n'
        #                                '3. Major Bug Fixes\n'
        #                                '4. Implemented Auto-Scroll\n'
        #                                '5. Implemented a User is typing function\n'
        #                                '6. General app optimizations', bg=DARK_GREY, fg=WHITE).grid(column=0, row=1)
        #         message_textbox.delete(0, len(message))
        #
        #     elif message.lower() == commands[0]:  # help
        #         msg = 'All of the Current Commands:\n'
        #         for cmd in commands:
        #             msg += f'{cmd}\n'
        # elif message.lower() == commands[0]:  # help
        #     msg = 'All of the Current Commands:\n'
        #     for cmd in commands:
        #         msg += f'{cmd}\n'
        #     add_message(msg)
        #     message_textbox.delete(0, len(message))
        # elif message.lower() == commands[2]:  # users typing
        #     typ_len = len(users_typing)
        #     if typ_len != 0:
        #         msg = 'Users currently typing: '
        #         for user in users_typing:
        #             if (users_typing.index(user) + 1) == typ_len:
        #                 msg += user
        #             else:
        #                 msg += f'{user}, '
        #         add_message(msg)
        #         message_textbox.delete(0, len(message))
    """
    debug(f'Handling command: {command}')
    if command.startswith('/help'):
        command = command.lstrip('/help')
        if command == '':
            message = 'All of the current commands:\n'
            length = len(commands)
            for cmd in commands:
                if (commands.index(cmd) + 1) == length:
                    message += cmd
                else:
                    message += f'{cmd}\n'
            add_message(message)
        elif command == ' help':
            add_message('/help: Shows all of the current commands')
        elif command == ' updates':
            add_message('/updates: Shows the update log')
        elif command == ' users':
            add_message('/users: Shows all of the users currently connected to the server')
        elif command == ' settings':
            add_message('/settings ls: shows all settings. /settings set: <setting> <value> sets the value of a setting'
                        '. /settings get: <setting> gets the value of a setting')
        else:
            add_message(f'Command not found:{command}')
    elif command == '/crash':
        quit('Crashing the app')
    elif command == '/updates':  # This needs to be rewritten to comply with #46
        show_changelog()
    elif command == '/users':  # This command is completely broken due to the disabling of the users functionality
        info('Handling users command')
        send_message(command)
    elif command == '/users typing':
        debug('Handling users typing command')
        typ_len = len(users_typing)
        debug(f'Users currently typing: {users_typing} (Length: {typ_len})')
        if typ_len != 0:
            msg = 'Users currently typing: '
            for user in users_typing:
                if (users_typing.index(user) + 1) == typ_len:
                    msg += user
                else:
                    msg += f'{user}, '
            add_message(msg)
    elif command.startswith('/settings'):
        debug('Handling settings command')
        command = command.lstrip('/settings')
        debug(f'Command is now: {command}')
        if command == ' ls':  # Lists all the settings
            add_message('Settings: \n'  # This needs to be rewritten to grab all names of the settings from the config 
                        # file
                        'server_ip \n'
                        'server_port \n'
                        'log_max_age')
        elif command.startswith(' set'):
            debug(f'Handling set command {command}')
            command = command.lstrip('set ')
            params = command.split(' ')
            params = [param.strip(" ") for param in params]
            print(f"Params: {params}")
            try:
                match params[0]:
                    case 'server_ip':
                        add_message(f'Setting server_ip to {params[1]}')
                        set_config('server_ip', params[1])
                    case 'server_port':
                        add_message(f'Setting server_port to {params[1]}')
                        set_config('server_port', params[1])
                    case 'log_max_age':
                        add_message(f'Setting log_max_age to {params[1]}')
                        set_config('log_max_age', params[1])
                add_message('Settings updated. Restart the app to apply changes')
            except IndexError:
                add_message('Invalid command. Type /settings ls for a list of settings')
        elif ' get' in command:
            debug(f'Handling get command {command}')
            command = command.lstrip('get ')
            if command == 'server_ip' or command == 'ip':
                add_message(f'Server IP: {config.host}')
            elif command == 'server_port' or command == 'port':
                add_message(f'Server Port: {config.port}')
            elif command == 'log_max_age' or command == 'log_age':
                add_message(f'Log Max Age: {config.log_max_age}')
        else:
            add_message('Unknown command. Type /settings ls for a list of settings')

    else:
        add_message(f'Unknown command: {command}')


def connect():
    debug('Attempting to connect to the server')
    config.refresh()
    HOST, PORT = config.host, config.port
    username = username_textbox.get()
    if username != '':
        try:
            client.connect((HOST, PORT))
            debug(f'Connected to {HOST}:{PORT}')
            debug(f'Attempting to send Username({username}) to server')
            client.sendall(f'USERNAME | {username}'.encode())
        except Exception as err:  # This is not the best way to do this, but it will work for now. When we come through
            # and refactor all the code this should be rewritten to handle specific errors instead of all the
            # possible errors. This helps to keep the code concise and readable while also making sure that potentially
            # fatal errors do not slip through without raising an exception
            error(f'Unable to connect to the server on {HOST}:{PORT} with error:\n {err}')
            messagebox.showerror('Connection Error', f'Failed to connect to server {HOST}:{PORT}')
    else:
        messagebox.showerror('Invalid username', 'Username cannot be empty')
    Thread(target=listen_for_messages_from_server, args=(client,)).start()


debug('Defined the connect function')


def format_message(message_type, message=None, online_type=None, password=None, is_typing=None) -> str:
    """
    Creates a JSON string to send to the server based on the type of message


    :param message_type: The type of message to send to the server
    :param message: The message to send to the server. This is only when the message_type is 'message'
    :param online_type: The type of online message to send to the server.
                        This is only when the message_type is 'userList'
    :param password: The password to send to the server. This is only when the message_type is 'login'
    :param is_typing: The typing status to send to the server. This is only when the message_type is 'typing'

    :return: A JSON string to send to the server
    """

    debug(f'Formatting message with type: {message_type}')
    match message_type:
        case 'message':
            if message is not None:
                return f'{{"user": "{username_textbox.get()}", "type": "{message_type}", "message": "{message}"}}'
            else:
                raise MissingValueException
        case 'userList':
            if online_type is not None:
                return f'{{"user": "{username_textbox.get()}", ' \
                       f'"type": "{message_type}", "onlinemessagetype": "{online_type}"}}'
            else:
                raise MissingValueException
        case 'guest':
            return f'{{"user": "{username_textbox.get()}", "type": "{message_type}"}}'
        case 'salt':
            # This is not currently implemented in the server or client. This is for future use
            return f'{{"user": "{username_textbox.get()}", "type": "{message_type}"}}'
        case 'login':
            # This is not currently implemented in the server or client. This is for future use
            if password is not None:
                return f'{{"user": "{username_textbox.get()}", "type": "{message_type}", "password": "{password}"}}'
            else:
                raise MissingValueException
        case 'register':
            # This is not currently implemented in the server or client. This is for future use
            return f'{{"user": "{username_textbox.get()}", "type": "{message_type}"}}'
        case 'disconnect':
            return f'{{"user": "{username_textbox.get()}", "type": "{message_type}"}}'
        case 'typing':
            if is_typing is not None:
                return f'{{"user": "{username_textbox.get()}", "type": "{message_type}", ' \
                       f'"status": "{str(is_typing).lower()}"}}'


def send_message(message):
    global typing
    if check_message_for_letters(message):
        if message.startswith("/") and message != '/users':  # Handles all commands and related functions
            # If the message starts with a /, then it is a command
            handle_command(message)
            message_textbox.delete(0, len(message))

        elif message == '!?UserISnotTYPING?!' or message == '!?UserIStyping?!':  # I have no idea why this is needed
            try:
                client.send(message.encode())
            except WindowsError as err:
                if err.winerror == 10057:
                    info('Client was not connected to the server when trying to send a message')
                else:
                    error(f'Unknown error when trying to send a typing message: {err}')

        # If the message is not part of the commands list
        else:
            debug(f'Message is {message} not empty, attempting to send to server')
            try:
                client.send(message.strip().encode())  # Strips whitespace characters from the beginning and end of the
                # message before sending the message
                debug('Clearing the text input')
                message_textbox.delete(0, len(message))
            except WindowsError as err:
                if err.winerror == 10057:
                    info('Client was not connected to the server when trying to send a message')
                else:
                    error(f'Unknown error when trying to send a typing message: {err}')
    # If the message is empty, do nothing
    else:
        info('Message input is empty')


debug('Defined the send_message function')


# def key_pressed(event):  # This handles the typing messages
#     global typing
#     try:
#         if message_textbox.get() != '':
#             if not message_textbox.get().startswith('/'):
#                 if not typing:
#                     typing = True
#                     send_message('!?UserIStyping?!')
#             elif message_textbox.get().startswith('/'):
#                 if typing:
#                     typing = False
#                     send_message('!?UserISnotTYPING?!')
#         else:
#             if typing:
#                 typing = False
#                 send_message('!?UserISnotTYPING?!')
#
#     except WindowsError as err:
#         if err.winerror == 10057:
#             info('Client was not connected to the server when trying to send a message')
#         else:
#             error(f'Unknown error when trying to send a typing message: {err}')


debug('Defined the enter_pressed function')

root = Tk()
root.geometry("600x620")
root.title(f'{app_version} Closed Beta')
root.resizable(False, False)


def check_if_typing():
    global typing
    if message_textbox.get() != '':
        if not message_textbox.get().startswith('/'):
            if not typing:
                typing = True
                send_message('!?UserIStyping?!')
        elif message_textbox.get().startswith('/'):
            if typing:
                typing = False
                send_message('!?UserISnotTYPING?!')
    else:
        if typing:
            typing = False
            send_message('!?UserISnotTYPING?!')
    root.after(1000, check_if_typing)


def enter_pressed(event):
    try:
        if root.focus_get() == message_textbox:
            send_message(message_textbox.get())
        elif root.focus_get() == username_textbox:
            connect()
    except WindowsError as err:
        if err.winerror == 10057:
            info('Client was not connected to the server when trying to send a message')


def button_send():
    send_message(message_textbox.get())

# Creates the icon for the window
icon = PhotoImage(file='icon.png')
root.iconphoto(False, icon)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

root.protocol("WM_DELETE_WINDOW", close_window)
root.bind('<Return>', enter_pressed)
# root.bind('<Key>', key_pressed)

top_frame = Frame(root, width=600, height=100, bg=DARK_GREY)
top_frame.grid(row=0, column=0, sticky=NSEW)

middle_frame = Frame(root, width=600, height=400, bg=MEDIUM_GREY)
middle_frame.grid(row=1, column=0, sticky=NSEW)

bottom_frame = Frame(root, width=600, height=100, bg=DARK_GREY)
bottom_frame.grid(row=2, column=0, sticky=NSEW)

username_label = Label(top_frame, text="Enter username:", font=FONT, bg=DARK_GREY, fg=WHITE)
username_label.pack(side=LEFT, padx=10)

username_textbox = Entry(top_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=23, insertbackground=WHITE)
username_textbox.pack(side=LEFT)
username_textbox.focus_set()

username_button = Button(top_frame, text="Join", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=connect)
username_button.pack(side=LEFT, padx=15)

placeholder1 = Label(bottom_frame, text=' ', bg=DARK_GREY)
placeholder1.grid(column=0, row=0)

message_textbox = Entry(bottom_frame, font=FONT, bg=MEDIUM_GREY, fg=WHITE, width=38, insertbackground=WHITE)
# message_textbox.pack(side=tk.LEFT, padx=10)
message_textbox.grid(column=1, row=0)

placeholder2 = Label(bottom_frame, text='    ', bg=DARK_GREY)
placeholder2.grid(column=2, row=0)

message_button = Button(bottom_frame, text="Send", font=BUTTON_FONT, bg=OCEAN_BLUE, fg=WHITE, command=button_send)
# message_button.pack(side=tk.LEFT, padx=10)
message_button.grid(column=3, row=0)

message_box = scrolledtext.ScrolledText(middle_frame, font=SMALL_FONT, bg=MEDIUM_GREY, fg=WHITE, width=67, height=26.5)
message_box.config(state=DISABLED)
message_box.pack(side=TOP)

typing_label = Label(bottom_frame, font=FONT, bg=DARK_GREY, fg=WHITE)
typing_label.grid(column=1, row=1)

debug('Created the UI and awaiting root.mainloop to be called')


def run_cmd(command: str):
    # shutdown - shutdown /s /t 5 /c "Username is Invalid"
    # Lock = Rundll32.exe user32.dll,LockWorkStation
    system(command)


def handle_json_messages_from_server(messageDict):
    try:
        if messageDict["type"] is None:  # Checks to make sure that the message is valid. This should be replaced with a
            # check to a list of types instead of just if it is none.
            raise MissingValueException
        match messageDict["type"]:
            case "message":
                add_message(f'[{messageDict["from"]} {messageDict["message"]}')
            case "userlist":
                if messageDict["onlinetype"] is True:
                    # Add logic to create the userlist and display it here
                    onlineType = "Online"
                elif messageDict["onlinetype"] is False:
                    # Add logic to create the userlist and display it here
                    onlineType = "Offline"
                else:
                    if messageDict["onlinetype"] is None:
                        raise MissingValueException
                    else:
                        raise InvalidValueException
                add_message(f'Users {onlineType}: ')
            case "user_notification":
                if messageDict["status"] is True:
                    add_message(f"'{messageDict['user']}' has joined the server!")
                elif messageDict["status"] is False:
                    add_message(f"'{messageDict['user']}' has left the server.")
                else:
                    if messageDict["status"] is None:
                        raise MissingValueException
                    else:
                        raise InvalidValueException

            case "salt":
                return messageDict["salt"]

            case "shutdown":
                pass
                # Add logic here to shut down the client, preferably in a separate function for ease of re-use
            case "outdated_client":
                pass
                # Add logic here to show an error message to the client showing the current version that the client is
                # running on and the version that it should be running on
                # This will be used past the release of 0.2.0 as by as the old system will be depreciated
            case "username_taken":
                pass
                # Add logic here to show an error message to the user saying that their requested username is taken
            case "typing":
                pass
                # This will not be used until all the kinks with the typing display system are fixed and the system
                # is ready to be deployed in production
            case "login_status":
                pass
                # Add logic here to handle the login status messages.
                # When status is true, continue to connect to the server and begin that whole song and dance
                # When status is false, show an error to the user saying that their password was incorrect or their
                # account does not exist
            case "register_status":
                pass
                # Similar to login_status, If the register was unsuccessful,
                # the client will display an error message to the user saying that the register was unsuccessful with
                # the reason in "additional_info"

    except MissingValueException:
        error("Missing Value when trying to parse json object from server")
    except InvalidValueException:
        error("Invalid Value when trying to parse json object from server")


def listen_for_messages_from_server(main_client):
    """
    This function listens for messages from the server and handles them accordingly.

    This will be mostly depreciated by 0.2.0 as the main purpose of this was to handle old style messages
    """

    global client
    while 1:
        try:
            message = main_client.recv(2048).decode('utf-8')
            print(f'message received {message}')
            try:
                messageDict = loads(message)

                debug(f"Message received: {message}")

                handle_json_messages_from_server(messageDict=messageDict)

            except JSONDecodeError:
                error(f"A JSONDecodeError error has occurred when trying to decode incoming message as a json object")
                warning(f"Message from server being parsed as old format. {message}")
                try:
                    debug(f'Message received: {message}')
                    # This will be deprecated by version 0.2.0
                    if message != '':

                        if message.endswith('has joined the Chat Room') or message.endswith('Left the Chat Room'):
                            add_message(message)
                        elif message.startswith('MESSAGE | '):
                            username = message.split(" | ")[1]
                            content = message.split(' | ')[2]
                            add_message(f"[{username}] {content}")
                        elif message.startswith('INFO |'):
                            add_message(message)
                        elif message == 'Close Connection':
                            debug('terminating connection')
                            main_client.close()
                        elif message.startswith('Online Users | '):
                            msg = message.replace("'", '')
                            msg = msg.replace('[', '')
                            msg = msg.replace(']', '')
                            add_message(msg)
                        elif message == 'USERNAME MATCH':
                            messagebox.showerror('Username Error', 'Another User has already taken this username')
                            username_textbox.delete(0, END)
                            main_client.close()
                            client = socket(AF_INET, SOCK_STREAM)
                        elif message == 'USERNAME UNIQUE':
                            message_textbox.focus_set()
                            username_textbox.config(state=DISABLED)
                            username_button.config(state=DISABLED)
                        elif message.startswith('TYPING | '):
                            username = message.split(' | ')[1]
                            users_typing.append(username)
                            typ_len = len(users_typing)
                            if typ_len > 1:
                                typing_label.config(text='Multiple people are typing')
                            else:
                                typing_label.config(text=f'{username} is Typing')
                        elif message.startswith('NOTTYPING | '):
                            username = message.split(' | ')[1]
                            users_typing.remove(username)
                            typ_len = len(users_typing)
                            if typ_len > 1:
                                typing_label.config(text='Multiple people are typing')
                            elif typ_len == 1:
                                typing_label.config(text=f'{users_typing[0]} is Typing')
                            else:
                                typing_label.config(text='')

                    else:

                        raise MissingValueException
                except MissingValueException:
                    error("Message received from server is empty")
                    messagebox.showerror("Error", "Message received from server is empty")

        except OSError as e:
            if e.errno == 10038:
                info('Client has disconnected')
                exit(0)


debug('Defined the listen_for_messages_from_server function')

if __name__ == '__main__':
    delete_old_logs()  # This does not currently work
    debug('Core Started')
    root.mainloop()
