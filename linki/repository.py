from urllib.parse import ParseResult, urlparse
from linki.article import ArticleCollection
from linki.connection import Connection, PathConnection
from linki.draft import DraftCollection
from linki.subscription import SubURLCollection
from linki.title import TitleCollection


class RepositoryConnection:
    url: ParseResult

    def __init__(self, url: str) -> None:
        self.url = urlparse(url)

    def get_style(self, style: str) -> Connection:
        match self.url.scheme:
            case 'file':
                path = PathConnection.get_path(self.url.path, style)
                return PathConnection(path)
            case 'ssh':
                raise NotImplementedError
            case 'http':
                raise NotImplementedError
            case _:
                raise NotImplementedError

    def create_style(self, style: str):
        match self.url.scheme:
            case 'file':
                PathConnection.create_path(self.url.path, style)
            case 'ssh':
                raise NotImplementedError
            case 'http':
                raise NotImplementedError
            case _:
                raise NotImplementedError


class Repository:
    styles = {'titles', 'subs', 'drafts', 'articles'}

    def __init__(self, url: str) -> None:
        self.connection = RepositoryConnection(url)

    @property
    def titles(self) -> TitleCollection:
        connection = self.connection.get_style('titles')
        return TitleCollection(connection)

    @property
    def subs(self) -> SubURLCollection:
        connection = self.connection.get_style('subs')
        return SubURLCollection(connection)

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
