from abc import ABC
from dataclasses import dataclass
from pathlib import Path

from sigili.article.content.repository import ContentRepository, FileSystemContentRepository, MemoryContentRepository
from sigili.article.group.repository import FileSystemGroupRepository, GroupRepository, MemoryGroupRepository
from sigili.article.history.repository import FileSystemHistoryRepository, HistoryRepository, MemoryHistoryRepository
from sigili.connection import Connection, MemoryConnection, PathConnection
from sigili.type.id import ArticleID, BlankArticleID, ContentID, Label


@dataclass
class ArticleUpdate():
    title: str
    content: bytes
    groups: list[str]
    editOf: ArticleID = BlankArticleID

    @classmethod
    def createUpdate(cls, article: 'Article', content: bytes) -> 'ArticleUpdate':
        _groups = [label.name for label in article.groups]
        return cls(
            article.title.name,
            content,
            _groups,
            article.editOf
        )


@dataclass
class Article():
    title: Label
    articleId: ArticleID
    contentId: ContentID
    groups: list[Label]
    editOf: ArticleID = BlankArticleID

    @classmethod
    def fromArticleUpdate(cls, update: ArticleUpdate) -> 'Article':
        _title = Label(update.title)
        _articleId = ArticleID.getArticleID(update)
        _contentId = ContentID.getContentID(update.content)
        _groups = [Label(_group) for _group in update.groups]
        if (update.editOf is None):
            return cls(
                _title,
                _articleId,
                _contentId,
                _groups,
            )
        return cls(
            _title,
            _articleId,
            _contentId,
            _groups,
            update.editOf
        )


class ArticleRepository(ABC):
    _articles: Connection
    _content: ContentRepository
    _history: HistoryRepository
    _groups: GroupRepository

    @property
    def groups(self) -> GroupRepository:
        return self._groups

    @property
    def content(self) -> ContentRepository:
        return self._content

    @property
    def history(self) -> HistoryRepository:
        return self._history

    def add_article(self, update: ArticleUpdate) -> Article:
        newArticle = Article.fromArticleUpdate(update)
        self._content.add_content(update.content)
        for group in update.groups:
            self._groups.add_to_group(newArticle.articleId, group)
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
        self._history.add_edit(newArticle.editOf, newArticle.articleId)

        return newArticle

    def get_articleIds(self) -> set[ArticleID]:
        return {ArticleID(_article) for _article in self._articles}

    def get_update(self, articleId: ArticleID) -> ArticleUpdate:
        _article = self._articles[articleId]
        _content = self._content.get_content(_article.contentId)
        return ArticleUpdate.createUpdate(_article, _content)

    def merge_article(self, update: ArticleUpdate) -> Article:
        if (self.has_article(update.editOf)):
            return self.update_article(update)
        return self.add_article(update)


class MemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._articles = MemoryConnection[Article]()
        self._content = MemoryContentRepository()
        self._history = MemoryHistoryRepository()
        self._groups = MemoryGroupRepository()


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, paths: dict[str, Path]):
        if (not paths['articles'].exists()):
            raise FileNotFoundError(
                f'Articles folder not found in repository. The folder might not be initialized.')

        self._articles = PathConnection[Article](paths['articles'])
        self._content = FileSystemContentRepository(paths['content'])
        self._history = FileSystemHistoryRepository(paths['history'])
        self._groups = FileSystemGroupRepository(paths['groups'])

    @staticmethod
    def get_paths(path: Path) -> dict[str, Path]:
        return {
            'articles': path.joinpath('articles').resolve(),
            'content': path.joinpath('content').resolve(),
            'history': path.joinpath('history').resolve(),
            'groups': path.joinpath('groups').resolve()
        }

    @classmethod
    def init(cls, path: Path) -> dict[str, Path]:
        _articlePath = path.joinpath('articles')
        _articlePath.mkdir()
        FileSystemContentRepository.initialize_directory(path)
        FileSystemHistoryRepository.initialize_directory(path)
        FileSystemGroupRepository.initialize_directory(path)
        return cls.get_paths(path)

    @classmethod
    def fromPath(cls, path: Path) -> ArticleRepository:
        paths = cls.get_paths(path)
        return cls(paths)
