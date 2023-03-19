import socket
import hashlib
import secrets


def send(data):
    client_socket.sendall(data.encode())
    reply = client_socket.recv(1024).decode()
    print(reply)
    return reply


def createHash(tempPassword: str, salt: str) -> str:
    # Combine password and salt
    passwordAndSalt = tempPassword + salt
    # Remove tempPassword
    del tempPassword

    hashedPassword = hashlib.sha256(passwordAndSalt.encode()).hexdigest()

    return hashedPassword


def checkPresence(username, param1, param2):
    return send(f"checkPresence('{username}', '{param1}', '{param2}')")


def addItem(username, password, salt, param):
    return send(f"addItem('{username}', '{password}', '{salt}', '{param}')")


def addUser(username: str, password: str):
    # Generate a random salt value using the hex module
    salt = secrets.token_hex(32)
    hashedPassword = createHash(password, salt)

    if checkPresence(username, "users", "username"):
        print("This user already exists! ")
        return

    addItem(username, password, salt, "users")

    print(salt)
    print(hashedPassword)
    print(len(hashedPassword))


def getItemFromUsername(username, param):
    return send(f"getItemFromUsername('{username}', '{param}')")


def login(username: str, password: str):
    if checkPresence(username, "users", "username") is not True:
        print("This username does not exist in our database. ")
        return

    hashedPassword = createHash(password, getItemFromUsername(username, "salt"))

    if hashedPassword == getItemFromUsername(username, "password"):
        print("Logged In Successfully! ")


if __name__ == '__main__':
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect(('localhost', 1234))


    print("Welcome to NAME_HERE.")
    while 1:
        action = input("Please input the action that you want to perform. Options: login, signup        ")
        match action:
            case "login":
                login(input("Username: "), input("Password: "))  # TODO: Hide the password when the user is inputting it
            case "signup":
                addUser(input("Username: "), input("Password: "))  # TODO: Hide the password when the user is inputting it
            case "exit":
                send("[Disconnect]")
                exit("done")

