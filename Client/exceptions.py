"""
This file defines all the exceptions and errors that can be raised in Client.py
"""


class MessageHandlerException(Exception):
    """
    Used for general message handler errors.
    """


class MissingValueException(MessageHandlerException):
    """
    Raised when a value is missing that is required for a function to work properly
    """

    def __init__(self, message="Missing value when trying to parse server message"):
        self.message = message
        super().__init__(self.message)


class InvalidValueException(MessageHandlerException):
    """
    Raised when a value is provided but is not in expected possible cases.
    """

    def __init__(self, message="Invalid value when trying to parse server message"):
        self.message = message
        super().__init__(self.message)


class OutdatedClientException(Exception):
    """
    Raised when the client is outdated.
    """

    def __init__(self, message="Outdated client"):
        self.message = message
        super().__init__(self.message)


class LoginHandlingException(Exception):
    """
    General exception class for login related errors. Used for any misc errors
    """
    pass


class UsernameTakenException(LoginHandlingException):
    """
    Raised when a username is already taken
    """

    def __init__(self, message="Username is already taken in server database."):
        self.message = message
        super().__init__(self.message)


class IncorrectPasswordException(LoginHandlingException):
    """
    Raised when the user inputs the incorrect password.
    """

    def __init__(self, message="Incorrect password when trying to sign in"):
        self.message = message
        super().__init__(self.message)


class TypingStatusException(Exception):
    """
    General exception class for typing status errors. Used for any misc errors
    """
    pass
