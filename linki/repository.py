from pathlib import Path
from typing import Dict, Iterable, List
from urllib.parse import ParseResult

import msgspec
from linki.article import Article, ArticleCollection
from linki.connection import MemoryConnection, ROWebConnection, Connection, PathConnection
from linki.draft import DraftCollection
from linki.id import ID
from linki.url import URL, URLCollection
from linki.title import Title, TitleCollection


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

    def get_collection(self, style: str):
        connection = self.connection.get_style(style)
        collection = MemoryConnection()
        for item in connection:
            collection[item] = connection[item]
        return collection

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
    def path(self) -> Path:
        return Path(self.connection.url.path)

    @classmethod
    def fromPath(cls, path: str | Path):
        path = Path(path).resolve().as_uri()
        return cls(path)

    @classmethod
    def createPath(cls, path: str | Path):
        path = Path(path).resolve().as_uri()
        return cls.create(path)


class MemoryRepoConnection(RepositoryConnection):
    def __init__(self) -> None:
        self.connections: Dict[str, MemoryConnection] = dict()

    def get_style(self, style: str) -> Connection:
        conn = self.connections.get(style)
        if conn is None:
            conn = MemoryConnection()
            self.connections[style] = conn
        return self.connections[style]


class TemporaryRepository(Repository):
    def __init__(self) -> None:
        self.connection = MemoryRepoConnection()

    @classmethod
    def fromStreams(cls, **streams: bytes):
        repo = cls()
        for stream in streams:
            if stream not in cls.styles:
                continue
            style = None
            if (stream == 'articles'):
                style = Article
            if (stream == 'titles'):
                style = Title
            if (style is None):
                continue
            items = msgspec.msgpack.decode(streams[stream], type=List[style])
            d_conn = repo.connection.get_style(stream)
            if (stream == 'articles'):
                for item in items:
                    d_conn[item.articleId] = item
            if (stream == 'titles'):
                for item in items:
                    d_conn[item.label.labelId] = item
        return repo
