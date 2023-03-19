import socket
import mysql.connector

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to a specific address and port
server_socket.bind(('localhost', 1234))

# Listen for incoming connections
server_socket.listen(5)

def send(data):
    client_socket.sendall(data.encode())
# This area of the code is dedicated to SQL stuff

# Connection Template
# cnx = mysql.connector.connect(
#         host="localhost",
#         user="dev",
#         password="developer",
#         database="world"
#     )
#     cursor = cnx.cursor()
# query = ""
# cursor.execute(query)
# cursor.close()
# cnx.close()

def showTable(table: str):
    cnx = mysql.connector.connect(
        host="localhost",
        user="dev",
        password="developer",
        database="world"
    )
    cursor = cnx.cursor()

    query = f"SELECT * from {table}"
    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    cnx.close()

def checkPresence(itemToCheck: str, table: str, column: str) -> bool:
    cnx = mysql.connector.connect(
        host="localhost",
        user="dev",
        password="developer",
        database="world"
    )
    cursor = cnx.cursor()

    query = f"SELECT * FROM {table} WHERE {column}='{itemToCheck}'"
    cursor.execute(query)

    result = cursor.fetchone()

    cursor.close()
    cnx.close()

    if result is None:
        return False
    else:
        return True

def addItem(username: str, password: str, salt: str, table: str):
    cnx = mysql.connector.connect(
        host="localhost",
        user="dev",
        password="developer",
        database="world"
    )
    cursor = cnx.cursor()

    query = f"INSERT INTO {table} (username, password, salt) VALUES (%s, %s, %s)"
    values = (username, password, salt)
    cursor.execute(query, values)
    cnx.commit()
    cursor.close()
    cnx.close()

def removeItem(item, table: str):
    confirm = input(f"Are you sure that you want to remove the item '{item} from {table}? y/n      ")
    if confirm != "y":
        return

    cnx = mysql.connector.connect(
        host="localhost",
        user="dev",
        password="developer",
        database="world"
    )
    cursor = cnx.cursor()

    query = f"DELETE FROM {table} WHERE username='{item}'"
    cursor.execute(query)

    cnx.commit()

    cursor.close()
    cnx.close()

def getItemFromUsername(username: str, item: str):
    cnx = mysql.connector.connect(
        host="localhost",
        user="dev",
        password="developer",
        database="world"
    )
    cursor = cnx.cursor()

    query = f"SELECT {item} FROM users WHERE username='{username}'"
    cursor.execute(query)

    result = cursor.fetchone()

    cursor.close()
    cnx.close()
    return result[0]


if __name__ == '__main__':
    while True:
        # Establish a connection with the client
        (client_socket, client_address) = server_socket.accept()

        while True:
            # Receive data from the client
            data = client_socket.recv(1024).decode()
            print(data)
            if data == "[Disconnect]":
                reply = "[Disconnect]"

            else:
                print(exec(data))
                reply = "None"

                # print(exec(data))
                # reply = exec(data)
            # match data.lower():
            #     case "showtable":
            #         showTable(input("Table: "))
            #     case "checkpresence":
            #         print(checkPresence(input("Item: "), input("Table: "), input("Column: ")))
            #     case "removeitem":
            #         removeItem(input("Item: "), input("Table: "))
            #     case "getsalt":
            #         print(getItemFromUsername(input("Username: "), input("Item: ")))

            # Send data back to the client
            send(reply)

