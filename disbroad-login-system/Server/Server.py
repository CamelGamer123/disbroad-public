from logging import basicConfig, DEBUG, CRITICAL, FileHandler, StreamHandler, info, error, debug
from datetime import datetime
from sys import stdout
from os import getcwd
import socket
import threading
from time import sleep

server_ip = ''
server_port = 0
connected_clients = []
client_limit = 0
address = None

dt = datetime.now().strftime("%d.%m.%Y")
basicConfig(
    level=DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s',
    handlers=[
        FileHandler(f'{getcwd()}/Logs/Debug/Debug_Log {dt}.txt'),
        StreamHandler(stdout)
    ]
)

def get_config():
    try:
        # This gets the config and is more readable than the previous method, it also automatically closes the file
        with open(f"{getcwd()}/config.txt", "r") as config:
            for line in config.readlines():
                if line.startswith('server_ip:'):
                    ip = str(line.split(': ')[1])
                    if ip == 'auto\n':
                        server_ip = socket.gethostbyname(socket.gethostname())
                    else:
                        server_ip = ip.split('\n')[0]
                    if server_ip != socket.gethostbyname(socket.gethostname()) and server_ip != 'localhost':
                        error(f'IP IS INVALID ({server_ip})')
                        exit(4)
                elif line.startswith('server_port:'):
                    server_port = int(line.split(': ')[1])
                    if not int(server_port):
                        error(f'PORT IS INVALID ({server_port})')
                        exit(5)
                elif line.startswith('max_clients:'):
                    client_limit = int(line.split(': ')[1])
                    if not int(client_limit):
                        error(f'CLIENT LIMIT IS INVALID ({client_limit})')
                        exit(3)
        debug(f'Grabbed config data from {getcwd()}/config.txt')
    except FileNotFoundError:
        error(f'Config file not found at {getcwd()}/config.txt')
        exit(6)
    return server_ip, server_port, client_limit



def find_user(client):
    for user in connected_clients:
        if user[1] == client:
            return user
def message_from_client(client, username):
    while 1:
        message = client.recv(2048).decode('utf-8')
        if message != '':
            debug(f"Message received: {message}")
            if message == 'Close Connection':
                debug('Client wishes to disconnect')
                user = find_user(client)
                debug('Found client in connected_clients')
                connected_clients.remove(user)
                debug('Removed Client from connected_clients')
                send_to_one(client, 'Close Connection')
                debug('Told the client to close application')
                msg_to_send = username + ' | Has left the Chat Room'
                send_to_all(msg_to_send)
                debug('Told all other clients that Client has disconnected')
            # elif message == 'Server Shutdown':
            #     print('shutting down')
            #     send_to_all('INFO | Server is shutting Down')
            #     sleep(0.1)
            #     send_to_all('Close Connection')
            #     sleep(2)
            #     quit()
            elif message == '/users':
                list_members(client)
            elif message == '!?UserIStyping?!':
                send_to_all(f'TYPING | {username}')
            elif message == '!?UserISnotTYPING?!':
                send_to_all(f'NOTTYPING | {username}')
            else:
                msg_to_send = 'MESSAGE | ' + username + ' | ' + message
                send_to_all(msg_to_send)


def send_to_one(client, message):
    client.sendall(message.encode())


def send_to_all(message):
    for user in connected_clients:
        send_to_one(user[1], message)


def list_members(client):
    online_users = 'Online Users | '
    for user in connected_clients:
        online_users += f'{user[0]}, '
        sleep(0.2)
    send_to_one(client, online_users)


def client_handler(client):
    data = client.recv(2048).decode('utf-8')
    while 1:
        if data != '':
            if data.startswith('USERNAME'):
                username = data.split(' | ')[1]
                match = False
                for user in connected_clients:
                    if username == user[0]:
                        match = True
                if match:
                    send_to_one(client, 'USERNAME MATCH')
                    sleep(0.1)
                    send_to_one(client, 'Close Connection')
                else:
                    send_to_one(client, 'USERNAME UNIQUE')
                    connected_clients.append((username, client))
                    sleep(0.1)
                    send_to_all(f'INFO | {username} has joined the Chat Room')
                    list_members(client)
                break
        else:
            error('Data is empty!')
    threading.Thread(target=message_from_client, args=(client, username, )).start()


# Replaced Main function creation and call with this
if __name__ == '__main__':

    # Gets all the required info from config
    address, server_port, client_limit = get_config()

    # Creates the Server instance
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Attempts to start the Server
    try:
        server.bind((server_ip, server_port))
        info(f' Server has started ({address}:{server_port})')
    except Exception as err:
        error(err)

    server.listen(client_limit)

    while 1:
        client, address = server.accept()
        info(f'Client ({address[0]}:{address[1]}) has connected to the Server!')

        threading.Thread(target=client_handler, args=(client, )).start()
