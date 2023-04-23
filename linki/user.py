
from linki.connection import Connection
from linki.id import BaseLabel


def Password(password):
    return BaseLabel.fromUnsafeString(password).labelId


class User():
    pass


class UserCollection():
    def __init__(self, connection: Connection[User]) -> None:
        self.store = connection

    def verify_user(self, username, password):
        user = self.store.get(Password(password))
        return user is not None

    def add_user(self, username, password):
        password = Password(password)
        self.store[password] = username
