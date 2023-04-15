from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse
from sigili.connection import Connection, PathConnection

from sigili.title.repository import TitleCollection


class RepositoryConnection:
    url: ParseResult

    def __init__(self, url: str) -> None:
        self.url = urlparse(url)

    def get_connection(self, style: str) -> Connection:
        match self.url.scheme:
            case 'file':
                path = PathConnection.get_path(self.url.geturl(), style)
                return PathConnection(path)
            case 'ssh':
                raise NotImplementedError
            case 'http':
                raise NotImplementedError
            case _:
                raise NotImplementedError


@dataclass
class Repository:
    connection: RepositoryConnection

    def __init__(self, url: str) -> None:
        self.connection = RepositoryConnection(url)

    @property
    def titles(self) -> TitleCollection:
        connection = self.connection.get_connection('titles')
        return TitleCollection(connection)
