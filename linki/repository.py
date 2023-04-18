from pathlib import Path
from typing import Iterable
from urllib.parse import ParseResult
from linki.article import ArticleCollection
from linki.connection import ROWebConnection, Connection, PathConnection
from linki.draft import DraftCollection
from linki.id import ID
from linki.url import URL, URLCollection
from linki.title import TitleCollection


class RepositoryConnection:
    url: ParseResult

    def __init__(self, url: str) -> None:
        self.url = URL(url).parsed

    def get_style(self, style: str) -> Connection:
        match self.url.scheme:
            case 'file':
                path = PathConnection.get_path(self.url.path, style)
                return PathConnection(path)
            case 'ssh':
                raise NotImplementedError
            case 'http' | 'https':
                return ROWebConnection(self.url, style)
            case _:
                raise NotImplementedError

    def create_style(self, style: str):
        match self.url.scheme:
            case 'file':
                PathConnection.create_path(self.url.path, style)
            case 'ssh':
                raise NotImplementedError
            case 'http' | 'https':
                raise NotImplementedError
            case _:
                raise NotImplementedError


class Repository:
    styles = {'titles', 'subs', 'contribs', 'drafts', 'articles'}

    def __init__(self, url: str) -> None:
        self.connection = RepositoryConnection(url)

    def get_item(self, style: str, item_id: ID):
        connection = self.connection.get_style(style)
        if (connection is None):
            return None
        if (item_id not in connection):
            return None
        return connection.get(item_id)

    def iter_item(self, style: str) -> Iterable[ID]:
        connection = self.connection.get_style(style)
        if (connection is None):
            return []
        return connection.keys()

    def get_count(self, style: str):
        connection = self.connection.get_style(style)
        if (connection is None):
            return 0
        return len(connection.keys())

    @property
    def titles(self) -> TitleCollection:
        connection = self.connection.get_style('titles')
        return TitleCollection(connection)

    @property
    def subs(self) -> URLCollection:
        connection = self.connection.get_style('subs')
        return URLCollection(connection)

    @property
    def contribs(self) -> URLCollection:
        connection = self.connection.get_style('contribs')
        return URLCollection(connection)

    @property
    def drafts(self) -> DraftCollection:
        connection = self.connection.get_style('drafts')
        return DraftCollection(connection)

    @property
    def articles(self) -> ArticleCollection:
        connection = self.connection.get_style('articles')
        return ArticleCollection(connection)

    @classmethod
    def create(cls, base: str):
        connection = RepositoryConnection(base)
        for style in cls.styles:
            connection.create_style(style)


class FileRepository(Repository):
    def __init__(self, url: str) -> None:
        super().__init__(url)
        if (self.connection.url.scheme != 'file'):
            raise ValueError

    @property
    def path(self) -> str:
        return self.connection.url.path

    @classmethod
    def fromPath(cls, path: str | Path):
        path = Path(path).resolve().as_uri()
        return cls(path)

    @classmethod
    def createPath(cls, path: str | Path):
        path = Path(path).resolve().as_uri()
        return cls.create(path)
