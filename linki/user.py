
from linki.connection import Connection
from linki.id import Label


def UserID(username, password):
    return Label([username, password]).labelId


class Contributor():
    pass


class ContributorExistsError(Exception):
    pass


class ContributorCollection():
    def __init__(self, connection: Connection[Contributor]) -> None:
        self.store = connection

    def verify_user(self, username: str | None, password: str | None):
        user = self.store.get(UserID(username, password))
        return user is not None

    def add_user(self, username, password):
        user_id = UserID(username, password)
        # TODO Write test first
        # if (self.verify_user(username, password)):
        #   raise UserExistsError
        self.store[user_id] = username
