from datetime import datetime  # Imports the date
from json import load, dump, decoder, dumps, loads
from logging import basicConfig, DEBUG, FileHandler, StreamHandler, info, error, debug  # Imports all required logging
from os import getcwd, path, makedirs  # This is used to get the current working directory
from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname  # Imports required sockets
from sys import stdout
from threading import Thread  # Only Thread is used so only need to import it
from time import sleep
from JSON_Handler import Handler
# from ssl import CERT_REQUIRED, PROTOCOL_TLS_SERVER, SSLContext
from atexit import register
from requests import post, HTTPError

connected_clients = []
users_typing = []

defaultConfig = {
    'server_ip': 'auto',
    'server_port': 81,
    'version': '0.1.4',
    'max_clients': 20,
    "discord_bot_token": "",
    "discord_channel_id": 1234567890
}

dt = datetime.now().strftime("%d.%m.%Y")
basicConfig(
    level=DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s',
    handlers=[
        FileHandler(f'{getcwd()}/Logs/Debug/Debug_Log {dt}.txt'),
        StreamHandler(stdout)
    ]
)

directory = getcwd()


class Config:
    """
    Stores the config data from the config file and provides a refresh method to update the data dynamically. This is
    useful for when the config file is changed while the program is running.
    """

    def __init__(self):
        info('Initializing Config object')
        self.server_ip = None
        self.server_port = None
        self.version = None
        self.client_limit = None

        self.refresh()

    def write(self, data):
        """
        Writes the data to the config file
        :param data: The data to write to the config file
        """
        with open(f'{directory}\\Server_Data\\config.json', 'w') as self.config:
            dump(data, self.config, indent=4)
        info(f'Wrote config data to {directory}\\Server_Data\\config.json')

    def rewrite(self):
        """
        Writes the default config data to the config file
        """
        with open(f'{directory}\\config.json', 'w') as self.config:
            dump(defaultConfig, self.config, indent=4)
        info(f'Wrote default config data to {directory}\\Server_Data\\config.json')

    def refresh(self):
        info('Refreshing config data')
        # Tries to grab the config data from the config file
        try:
            with open(f'{directory}\\Server_Data\\config.json', 'r') as self.config:
                data = load(self.config)
            info(f'Grabbed config data from {directory}\\Server_Data\\config.json')
        except FileNotFoundError:  # If the config file is not found, it will create one with the default values
            with open(f'{directory}\\Server_Data\\config.json', 'w') as self.config:
                self.rewrite()
            info(f'Created config file at {directory}\\Server_Data\\config.json')
            self.refresh()
            return
        except decoder.JSONDecodeError:
            with open(f'{directory}\\Server_Data\\config.json', 'w') as self.config:
                self.rewrite()
            info(f'Config file was corrupted, default config data was written to {directory}\\Server_Data\\config.json')
            self.refresh()
            return

        # Check if the config sets the server IP to auto
        if data['server_ip'] == 'auto':
            data['server_ip'] = gethostbyname(gethostname())
        self.server_ip = data['server_ip']
        self.server_port = data['server_port']
        self.version = data['version']
        self.client_limit = int(data['max_clients'])

        info(
            f"Config data: IP: {self.server_ip}, Port: {self.server_port}, Version: {self.version}, Max Clients: "
            f"{self.client_limit}")


config = Config()
handler = Handler()
server_version = f'Disbroad Server V{config.version}'

# Check if the following folder and files exist, if not, create them
if not path.exists(f'{directory}/Server_Data'):
    makedirs(f'{directory}/Server_Data')
    info(f'Created folder {directory}/Server_Data')
if not path.exists(f'{directory}/Server_Data/Banned_Users.json'):
    with open(f'{directory}/Server_Data/Banned_Users.json', 'w') as banned_users:
        dump({}, banned_users, indent=4)
    info(f'Created file {directory}/Server_Data/Banned_Users.json')
if not path.exists(f'{directory}/Server_Data/Users.json'):
    with open(f'{directory}/Server_Data/Users.json', 'w') as users:
        dump({}, users, indent=4)
    info(f'Created file {directory}/Server_Data/Users.json')


def check_client_against_ip(client):
    """
    Used to check if the client object provided is associated with the correct username it claims to be. This is done to
    prevent forging messages that appear to be from user1 when in reality they are from user2 or even from a user that
    is not registered in the system.
    """

    # Get the username of the client
    username = find_user(client)[0]

    # Get the IP address of the client
    ip = client.getpeername()[0]

    # The ip address associated with the client when they are added to the system needs to be added to the returns of
    # find_user() before this can be implemented. DO NOT USE client.getpeername() TO RETURN THE IP, IT NEEDS TO BE
    # ASSOCIATED WITH THE CLIENT OBJECT


def find_user(client):
    """
    This function is used to find a user in the connected_clients list.
    """
    for user in connected_clients:
        if user[1] == client:
            return user


def format_message(message_type, message=None, client_list=None, username=None):
    """
    This function is used to format a message to be sent to the client.
    """
    match message_type:
        case 'shutdown':
            return f'{{"type":"shutdown"}}'
        case 'userlist':
            if client_list is not None:
                # This is the old way of doing it
                client_usernames = []
                for user in client_list:
                    client_usernames.append(user[0])
                return dumps({"type": "userlist", "users": client_usernames})

                # This will be the new way of doing it
                # return dumps({"type": "userlist", "users": list_members()})
            else:
                error('client_list is None')
        case 'salt':
            # The mySQL database will be used to store the salt and retrieve it when needed. This is just a placeholder
            salt = 54246512387541342385231564821532  # This is a placeholder
            return dumps({"type": "salt", "salt": salt})
        case 'login':
            # This is a placeholder for the login success message
            return dumps({"type": "login", "success": "This feature is not yet implemented"})
        case 'message':
            if message is not None and username is not None:
                return dumps(
                    {"type": "message", "from": username, "message": message})  # The username will be added later
            else:
                error('message or username is None')


def check_client_connection():
    for client in connected_clients:
        try:
            client[1].send(b'')
            return True
        except WindowsError:
            return False, client





def message_from_client(client, username):
    """
    This function is used to handle messages from already connected clients. This does NOT handle new users connecting.

    :param client: The client that is sending the message
    :param username: The username of the client that is sending the message
    """
    while 1:
        try:
            message = client.recv(2048).decode('utf-8')
        except ConnectionResetError:
            info('A client has unexpectedly disconnected')

            conn, user = check_client_connection()
            if not conn:
                info(f'Unexpected user was {user[0]}')
                connected_clients.remove(user)
                debug(f'connected_clients: {connected_clients}')
            break
        try:
            message = loads(message)
        except decoder.JSONDecodeError:

            # error('Message is not JSON, likely an outdated client. Telling client to update')
            # send_to_one(client, format_message('update'))

            # error('JSON DECODE ERROR')
            pass
        if message != '':
            debug(f"Message received: {message}")
            if message == 'Close Connection':
                debug('Client wishes to disconnect')
                if find_user(client):
                    debug('Found client in connected_clients')
                    send_to_one(client, 'Close Connection')
                    debug('Told the client to close application')
                    connected_clients.remove(find_user(client))
                    debug('Removed Client from connected_clients')
                    sleep(0.1)
                    send_to_all(f'{username} | Left the Chat Room')
                    debug('Told all other clients that Client has disconnected')
                else:
                    error('USER WAS NOT FOUND')
            # elif message == 'Server Shutdown':
            #     print('shutting down')
            #     send_to_all('INFO | Server is shutting Down')
            #     sleep(0.1)
            #     send_to_all('Close Connection')
            #     sleep(2)
            #     quit()
            elif message == '/users':
                list_members(client)
                # send_to_one(client, format_message('userlist', client_list = connected_clients))  # This is the new
                # way of doing it
            # elif message == '!?UserIStyping?!':
            #     send_to_all(f'TYPING | {username}')
            #     sleep(0.1)
            # elif message == '!?UserISnotTYPING?!':
            #     send_to_all(f'NOTTYPING | {username}')
            #     sleep(0.1)
            elif message == 'PeacockLock':  # This is to stop people locking pcs without pushing a client update
                send_to_one(client, 'INFO | You lack the permissions to use this command')
            elif message == 'Shutdown@Server':
                print('shutting down')
                server_quit()
            else:
                msg_to_send = 'MESSAGE | ' + str(username) + ' | ' + str(message)
                send_to_all(msg_to_send)
                sleep(0.1)


def send_to_one(client, message):
    for user in connected_clients:
        if user[1] == client:
            username = user[0]
            debug(f'Sending to {username}: {message}')
    # user = find_user(client)
    # if user:
        # name = user[0]
        # debug(f'Sending to {name}: {message}')
    try:
        client.send(str(message).encode())
    except WindowsError as err:
        error(err)


def server_quit():
    """
    This function is used to shut down the server.
    """
    send_to_all('INFO | Server is shutting down')
    sleep(0.1)
    send_to_all('Close Connection')

    sleep(1)
    print('quitting')
    quit(KeyboardInterrupt)



def send_to_all(message):
    """
    This function is used to send a message to all connected clients.
    """
    for user in connected_clients:
        send_to_one(user[1], message)


def list_members(client):
    online_users = []
    for user in connected_clients:
        online_users.append(user[0])
    send_to_one(client, f'Online Users | {str(online_users)}')


def add_user_to_system(client, ip):
    """
    This function is used to add a user to the system and check if the username is unique. This does NOT handle any
    messages other than new users connecting to the server.

    :param client: The client that is being added to the system
    :param ip: The ip address of the client being added to the system
    """
    # Receives the username from the client
    try:
        data = client.recv(2048).decode('utf-8')
    except ConnectionResetError:
        info('A client has unexpectedly disconnected')
        conn, user = check_client_connection()
        if not conn:
            info(f'Unexpected user was {user[0]}')
            connected_clients.remove(user)
            debug(f'connected_clients: {connected_clients}')
        return
    while 1:
        try:
            data = loads(data)
            # This needs to be able to handle returns from the handler correctly
            handler.new_connection(data, ip)

        except decoder.JSONDecodeError:
            # info("A Json Decode Error has occurred when trying to decode incoming data from a client.")
            # info("This is likely due to an outdated client. Telling client to update")
            pass
        if data != '':
            if data.startswith('USERNAME'):
                username = data.split(' | ')[1]
                match = False
                for user in connected_clients:
                    if username == user[0]:
                        info("Client tried to connect with a username that already exists.")
                        match = True
                        break
                if match:
                    client.send(b'USERNAME MATCH')
                else:
                    client.send(b'USERNAME UNIQUE')
                    connected_clients.append((username, client, ip))
                    sleep(0.1)
                    try:
                        send_to_all(f'INFO | {username} has joined the Chat Room')
                    except ConnectionResetError:
                        error('ConnectionResetError')
                    sleep(0.1)
                    list_members(client)
                    debug(f'Added {username} to connected_clients, connected clients: {connected_clients}')
                break
        else:
            error('Data is empty!')
    # Starts a new thread for each client to handle messages from that client
    Thread(target=message_from_client, args=(client, username,)).start()


if __name__ == '__main__':
    try:
        register(server_quit)
        config = Config()
        # Gets all the required info from config
        address, server_port, client_limit = config.server_ip, config.server_port, config.client_limit

        # Creates the Server instance
        server = socket(AF_INET, SOCK_STREAM)

        # context = SSLContext(PROTOCOL_TLS_SERVER)
        # context.verify_mode = CERT_REQUIRED
        # context.check_hostname = True
        # context.load_default_certs()
        # server = context.wrap_socket(socket, server_hostname=address)

        # Attempts to start the Server
        try:
            server.bind((config.server_ip, config.server_port))
        except Exception as err:
            error(err)
        server.listen(config.client_limit)
        info(f"\n\nServer is online! IP is {config.server_ip}\n\n")

        while 1:
            client, address = server.accept()
            info(f'Client ({address[0]}:{address[1]}) has connected to the Server!')

            # Starts a new thread for each client that connects
            Thread(target=add_user_to_system, args=(client, address[0],)).start()
    except KeyboardInterrupt:
        server_quit()
