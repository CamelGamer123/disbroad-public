from json import load, dump, JSONDecodeError
from random import randint


class LoginHandler:
    def __init__(self):
        self.users = {
            0: {
                'username': 'admin',
                'password': 'admin'
            }
        }
        self.banned_users = {}
        self.banned_ips = {}
        self.load()

    def load(self):
        try:
            with open('users.json', 'r') as users:
                self.users = load(users)
        except FileNotFoundError:
            with open('users.json', 'w') as users:
                dump(self.users, users, indent=4)
        except JSONDecodeError:
            with open('users.json', 'w') as users:
                dump(self.users, users, indent=4)

    def save(self):
        with open('users.json', 'w') as users:
            dump(self.users, users, indent=4)

    def login(self, username, password):
        for user in self.users:
            if self.users[user]['username'] == username and self.users[user]['password'] == password:
                return True
        return False

    def get_uid(self, username):
        for user in self.users:
            if self.users[user]['username'] == username:
                return user
        return None

    def add_user(self, username, password):
        self.users[randint(10000, 99999)] = {
            'username': username,
            'password': password
        }
        self.save()
