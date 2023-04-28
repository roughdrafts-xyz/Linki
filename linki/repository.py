from pathlib import Path
from typing import Dict, List
from urllib.parse import ParseResult

import msgspec
from linki.article import BaseArticle, ArticleCollection
from linki.config import ConfigCollection
from linki.connection import MemoryConnection, ROWebConnection, Connection, PathConnection
from linki.draft import DraftCollection, ShadowCollection
from linki.id import ID
from linki.change import ChangeCollection
from linki.url import URL, URLCollection
from linki.title import BaseArticle, TitleCollection
from linki.user import ContributorCollection


class RepositoryConnection:
    root: ParseResult
    url: ParseResult
    path: tuple[str]

    def __init__(self, url: str) -> None:
        self.url = URL(url).parsed
        match self.url.scheme:
            case 'file':
                # look upward until we find the root
                path = Path(self.url.path)
                root = None
                dot_path = Path('.')
                slash_path = Path('/')
                while (path != dot_path and path != slash_path):
                    if (path.joinpath('.linki').exists()):
                        root = URL(path.as_uri()).parsed
                        self.path = Path(self.url.path).relative_to(path).parts
                        break
                    path = path.parents[0]
                if (root is None):
                    raise FileNotFoundError(
                        '.linki folder not found. Maybe you need to initialize it?')
                self.root = root
            case 'https':
                # TODO Assumes installed to root path
                root = URL(url)
                root.parsed = root.parsed._replace(path='')
                root = root.parsed.geturl()
                self.root = URL(root).parsed

    def get_style(self, style: str) -> Connection:
        match self.root.scheme:
            case 'file':
                path = PathConnection.get_path(self.root.path, style)
                return PathConnection(path)
            case 'ssh':
                raise NotImplementedError
            case 'https':
                return ROWebConnection(self.root, style)
            case _:
                raise NotImplementedError

    def create_style(self, style: str):
        match self.root.scheme:
            case 'file':
                PathConnection.create_path(self.root.path, style)
            case 'ssh':
                raise NotImplementedError
            case 'https':
                raise NotImplementedError
            case _:
                raise NotImplementedError


class Repository:
    styles = {'titles', 'subs', 'contribs',
              'drafts', 'articles', 'users', 'changes', 'config'}

    def __init__(self, url: str) -> None:
        self.connection = RepositoryConnection(url)

    def __init_subclass__(cls, styles: set[str] | None = None) -> None:
        if (styles is not None):
            cls.styles |= styles

    def get_item(self, style: str, item_id: ID):
        connection = self.connection.get_style(style)
        if (connection is None):
            return None
        if (item_id not in connection):
            return None
        return connection.get(item_id)

    def get_collection(self, style: str):
        connection = self.connection.get_style(style)
        return list(connection.values())

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

    @property
    def users(self) -> ContributorCollection:
        connection = self.connection.get_style('users')
        return ContributorCollection(connection)

    @property
    def changes(self) -> ChangeCollection:
        connection = self.connection.get_style('changes')
        return ChangeCollection(connection)

    @property
    def config(self) -> ConfigCollection:
        connection = self.connection.get_style('config')
        return ConfigCollection(connection)

    @classmethod
    def create(cls, base: str):
        connection = RepositoryConnection(base)
        for style in cls.styles:
            connection.create_style(style)


class FileRepository(Repository, styles={'shadows'}):

    def __init__(self, url: str) -> None:
        super().__init__(url)
        if (self.connection.root.scheme != 'file'):
            raise ValueError

    @property
    def path(self) -> Path:
        return Path(self.connection.root.path).resolve()

    @classmethod
    def fromPath(cls, path: str | Path):
        path = Path(path).resolve().as_uri()
        return cls(path)

    @classmethod
    def createPath(cls, path: str | Path):
        Path(path).joinpath('.linki').mkdir(exist_ok=True)
        path = Path(path).resolve().as_uri()
        cls.create(path)

    @property
    def shadows(self) -> ShadowCollection:
        connection = self.connection.get_style('shadows')
        return ShadowCollection(connection)


class MemoryRepoConnection(RepositoryConnection):
    def __init__(self) -> None:
        self.connections: Dict[str, MemoryConnection] = dict()
        self.root = URL('').parsed
        self.url = URL('').parsed
        self.path = ('',)

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
                style = BaseArticle
            if (stream == 'titles'):
                style = BaseArticle
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
