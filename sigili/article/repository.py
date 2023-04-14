from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from sigili.connection import Connection, MemoryConnection, PathConnection
from sigili.type.id import ArticleID, Label


@dataclass
class Article():
    articleId: ArticleID
    label: Label
    content: bytes
    editOf: 'Article' | None

    def __init__(self, label: str, content: bytes, editOf: 'Article' | None) -> None:
        self.label = Label(label)
        self.content = content
        self.editOf = editOf
        self.articleId = ArticleID.getArticleID(
            self.label, self.content, self.editOf)


class ArticleRepository(ABC):
    _articles: Connection[Article]

    def merge_article(self, article: Article) -> Article:
        self._articles[article.articleId] = article
        return article

    def get_article(self, articleId: ArticleID) -> Article:
        if (self.has_article(articleId)):
            return self._articles[articleId]
        raise KeyError(
            'Article not found. Try using merge_article or add_article first.')

    def has_article(self, articleId: ArticleID | None) -> bool:
        return articleId in self._articles

    @staticmethod
    def fromURL(url: str | None = None):
        if (url is None):
            return MemoryArticleRepository()
        _url = urlparse(url)
        match _url.scheme:
            case 'file':
                return FileSystemArticleRepository(Path(_url.path))
            case 'ssh':
                raise NotImplementedError
            case 'http':
                raise NotImplementedError
            case _:
                raise NotImplementedError


class MemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._articles = MemoryConnection[Article]()


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, path: Path) -> None:
        self.articles = PathConnection(path.resolve())

    @staticmethod
    def init(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _articlePath = path.joinpath('articles')
        _articlePath.mkdir()
        return _articlePath
