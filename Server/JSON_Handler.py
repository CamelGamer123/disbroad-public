import json
import os


class Handler:
    """" 
    Handler for JSON requests from the client
    """

    def __init__(self):
        self.directory = os.getcwd()

    def new_connection(self, message, ip):
        # Check if the ip is banned
        if self.check_if_ip_banned(ip) or self.check_if_user_banned(message['username']):
            return {"type": "banned"}

        match message['type']:
            case 'login':
                # This will only be called if the user is trying to log in, not if they have already started
                # the register process
                if self.check_if_user_exists(message['username']):
                    if self.match_password(message['username'], message['password']):
                        return {"type": "login", "success": "true"}, \
                               {"type": "user_notification", "username": message['username'], "status": "true"}
                    else:
                        return {"type": "login", "success": "false"}

            case 'register':
                if self.check_if_user_exists(message['username']):
                    return {"type": "username_register_status", "taken": "true"}
                else:
                    return {"type": "username_register_status", "taken": "false"}
            case 'guest':
                if self.check_if_user_exists(message['username']):
                    return {"type": "username_register_status", "taken": "true"}
                else:
                    return {"type": "username_register_status", "taken": "false"}

                # check if the username is present in Users.json and that the username is not banned and that the
                # username is not in use by another guest client
                # if the username is present return {"type":"login", "success":"false"}
                # if the username is not present return {"type":"login", "success":"true"} and send a user_notification
                # to all clients in the form of
                # {"type":"user_notification", "username":message['username'], "status":"true"}

        """ 
        Called when a new connection is made
        """
        pass

    def handle_message(self, message):
        match message['type']:
            case 'salt':
                return self.get_salt(message['username'])
                # Check if the username is present in Users.json and that the username is not banned and that the user
                # has been trying to register in this session
                # if the username is present return {"type":"salt", "salt":self.get_salt(message['username'])}
                # if the username is not present but has been trying to register create a new user and salt and return
                # {"type":"salt", "salt":self.get_salt(message['username'])}
                # if the username is not present and has not been trying to register return {"type":"salt", "salt":None}
            case 'login':  # This will only be called if they have already started the register process
                if self.check_if_user_exists(message['username']):
                    if self.match_password(message['username'], message['password']):
                        return {"type": "login_status", "status": "success"}
                    else:
                        return {"type": "login_status", "status": "incorrect_password"}
                else:
                    return {"type": "login_status", "status": "user_not_found"}
                # Set the password in the Users.json file to the password sent by the client
            case 'disconnect':
                pass
                # Remove the user from the users list (NOT THE USERS.JSON FILE) and send a user_notification to all
                # clients in the form of {"type":"user_notification", "username":message['username'], "status":"false"}

            case 'userlist':
                pass
                # Return a list of all users matching the online status in the following format:
                # {"type":"userlist", "users":[user1, user2, user3, ...], "onlinetype":"true/false"}
            case 'message':
                pass
                # Send the message to all clients in the following format:
                # {"type":"message", "username":message['username'], "message":message['message']}
        """
        Called when a message is received from an existing connection
        """

    def check_if_user_exists(self, username):
        """
        This function is used to check if a user exists in the Users.json file.
        """
        with open(f'{self.directory}/Server_Data/Users.json', 'r') as users:
            data = json.load(users)
        return username in data

    def add_user(self, username, password, salt):
        """
        This function is used to add a user to the Users.json file.
        """
        with open(f'{os.getcwd()}/Server_Data/Users.json', 'r') as users:
            data = json.load(users)
        data[username] = {
            'password': password,
            'salt': salt
        }
        with open(f'{self.directory}Users.json', 'w') as users:
            json.dump(data, users, indent=4)

    def remove_user(self, username):
        """
        This function is used to remove a user from the Users.json file.
        """
        with open(f'{self.directory}/Server_Data/Users.json', 'r') as users:
            data = json.load(users)
        del data[username]
        with open(f'{self.directory}/Server_Data/Users.json', 'w') as users:
            json.dump(data, users, indent=4)

    def set_password(self, username, password):
        """
        This function is used to set the password of a user.
        """
        with open(f'{self.directory}/Server_Data/Users.json', 'r') as users:
            data = json.load(users)
        data[username]['password'] = password
        with open(f'{self.directory}/Server_Data/Users.json', 'w') as users:
            json.dump(data, users, indent=4)

    def ban_user(self, username):
        """
        This function is used to ban a user from the server.
        """
        with open(f'{self.directory}/Server_Data/Banned_Users.json', 'r') as banned_users:
            data = json.load(banned_users)
        data[username] = True
        with open(f'{self.directory}/Server_Data/Banned_Users.json', 'w') as banned_users:
            json.dump(data, banned_users, indent=4)

    def unban_user(self, username):
        """
        This function is used to unban a user from the server.
        """
        with open(f'{self.directory}/Server_Data/Banned_Users.json', 'r') as banned_users:
            data = json.load(banned_users)
        del data[username]
        with open(f'{self.directory}/Server_Data/Banned_Users.json', 'w') as banned_users:
            json.dump(data, banned_users, indent=4)

    def ban_ip(self, ip):
        """
        This function is used to ban an ip address from the server.
        """
        with open(f'{self.directory}/Server_Data/Banned_IPs.json', 'r') as banned_ips:
            data = json.load(banned_ips)
        data[ip] = True
        with open(f'{self.directory}/Server_Data/Banned_IPs.json', 'w') as banned_ips:
            json.dump(data, banned_ips, indent=4)

    def unban_ip(self, ip):
        """
        This function is used to unban an ip address from the server.
        """
        with open(f'{self.directory}/Server_Data/Banned_IPs.json', 'r') as banned_ips:
            data = json.load(banned_ips)
        del data[ip]
        with open(f'{self.directory}/Server_Data/Banned_IPs.json', 'w') as banned_ips:
            json.dump(data, banned_ips, indent=4)

    def check_if_user_banned(self, username):
        """
        This function is used to check if a user is banned.
        """
        with open(f'{self.directory}/Server_Data/Banned_Users.json', 'r') as banned_users:
            data = json.load(banned_users)
        return data[username]

    def check_if_ip_banned(self, ip):
        """
        This function is used to check if an ip address is banned.
        """
        with open(f'{self.directory}/Server_Data/Banned_IPs.json', 'r') as banned_ips:
            data = json.load(banned_ips)
        return data[ip]

    def get_salt(self, username):
        """
        This function is used to get the salt of a user.
        """
        with open(f'{self.directory}/Server_Data/Users.json', 'r') as users:
            data = json.load(users)
        return data[username]['salt']

    def match_password(self, username, password):
        """
        This function is used to match the password of a user.
        """
        with open(f'{self.directory}/Server_Data/Users.json', 'r') as users:
            data = json.load(users)
        return data[username]['password'] == password
