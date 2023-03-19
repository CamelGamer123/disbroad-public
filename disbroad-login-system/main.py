import hashlib
import secrets
import mysql.connector
import os

# Create Username and Password
username = "dev"
password = "developer"


def createHash(tempPassword: str, salt: str) -> str:
    # Combine password and salt
    passwordAndSalt = tempPassword + salt
    # Remove tempPassword
    del tempPassword

    hashedPassword = hashlib.sha256(passwordAndSalt.encode()).hexdigest()

    return hashedPassword


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


def login(username: str, password: str):
    if checkPresence(username, "users", "username") is not True:
        print("This username does not exist in our database. ")
        return

    hashedPassword = createHash(password, getItemFromUsername(username, "salt"))

    if hashedPassword == getItemFromUsername(username, "password"):
        print("Logged In Successfully! ")


def executeCommand(command: str):
    return os.system(command)


# This area of the code is dedicated to SQL stuff

# Connection Template
# cnx = mysql.connector.connect(
#         host="localhost",
#         user=username,
#         password=password,
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
        user=username,
        password=password,
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
        user=username,
        password=password,
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
        user=username,
        password=password,
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
        user=username,
        password=password,
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
        user=username,
        password=password,
        database="world"
    )
    cursor = cnx.cursor()

    query = f"SELECT {item} FROM users WHERE username='{username}'"
    cursor.execute(query)

    result = cursor.fetchone()

    cursor.close()
    cnx.close()
    return result[0]


# This area of the code is dedicated to UI
def devOptions():
    print("This section is for developers only!")
    while 1:
        devCmd = input("Please input the action that you want to perform. Options: login, signup, showTable, "
                       "checkPresence, removeItem, getSalt        ")
        match devCmd.lower():
            case "login":
                login(input("Username: "), input("Password: "))  # TODO: Hide the password when the user is inputting it
            case "signup":
                addUser(input("Username: "),
                        input("Password: "))  # TODO: Hide the password when the user is inputting it
            case "showtable":
                showTable(input("Table: "))
            case "checkpresence":
                print(checkPresence(input("Item: "), input("Table: "), input("Column: ")))
            case "removeitem":
                removeItem(input("Item: "), input("Table: "))
            case "getsalt":
                print(getItemFromUsername(input("Username: "), input("Item: ")))


if __name__ == '__main__':
    print("Welcome to NAME_HERE.")
    while 1:
        action = input("Please input the action that you want to perform. Options: login, signup        ")
        match action:
            case "login":
                login(input("Username: "), input("Password: "))  # TODO: Hide the password when the user is inputting it
            case "signup":
                addUser(input("Username: "),
                        input("Password: "))  # TODO: Hide the password when the user is inputting it
            case username:
                devOptions()
