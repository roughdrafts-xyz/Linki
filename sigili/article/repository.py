from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from sigili.connection import Connection, MemoryConnection, PathConnection
from sigili.type.id import ArticleID, BlankArticleID, Label


@dataclass
class ArticleUpdate():
    title: str
    content: bytes
    editOf: ArticleID = BlankArticleID

    @classmethod
    def fromArticle(cls, article: 'Article') -> 'ArticleUpdate':
        return cls(
            article.title.name,
            article.content,
            article.editOf
        )


@dataclass
class Article():
    title: Label
    content: bytes
    articleId: ArticleID
    editOf: ArticleID = BlankArticleID

    @classmethod
    def fromArticleUpdate(cls, update: ArticleUpdate) -> 'Article':
        _title = Label(update.title)
        _articleId = ArticleID.getArticleID(update)
        _content = update.content
        if (update.editOf is None):
            return cls(
                _title,
                _content,
                _articleId,
            )
        return cls(
            _title,
            _content,
            _articleId,
            update.editOf
        )


class ArticleRepository(ABC):
    _articles: Connection[Article]

    def add_article(self, update: ArticleUpdate) -> Article:
        newArticle = Article.fromArticleUpdate(update)
        self._articles[newArticle.articleId] = newArticle
        return newArticle

    def get_article(self, articleId: ArticleID) -> Article:
        if (self.has_article(articleId)):
            return self._articles[articleId]
        raise KeyError(
            'Article not found. Try using merge_article or add_article first.')

    def has_article(self, articleId: ArticleID | None) -> bool:
        return articleId in self._articles

    def update_article(self, update: ArticleUpdate) -> Article:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError(
                'Article must be an edit of another Article already in the Repository. Try using merge_article or add_article instead.')

        newArticle = self.add_article(update)

        return newArticle

    def get_articleIds(self) -> set[ArticleID]:
        return {ArticleID(_article) for _article in self._articles}

    def get_update(self, articleId: ArticleID) -> ArticleUpdate:
        _article = self._articles[articleId]
        return ArticleUpdate.fromArticle(_article)

    def merge_article(self, update: ArticleUpdate) -> Article:
        if (self.has_article(update.editOf)):
            return self.update_article(update)
        return self.add_article(update)

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
