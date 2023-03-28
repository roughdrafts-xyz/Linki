from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import pickle

from sigili.article.content.repository import ContentRepository, FileSystemContentRepository, MemoryContentRepository
from sigili.article.group.repository import FileSystemGroupRepository, GroupRepository, MemoryGroupRepository
from sigili.article.history.repository import FileSystemHistoryRepository, HistoryRepository, MemoryHistoryRepository
from sigili.type.id import ArticleID, BlankArticleID, ContentID, Label


@dataclass
class ArticleUpdate():
    title: Label
    content: bytes
    groups: list[str]
    editOf: ArticleID = BlankArticleID


@dataclass
class Article():
    title: Label
    articleId: ArticleID
    contentId: ContentID
    groups: list[str]
    editOf: ArticleID = BlankArticleID

    @staticmethod
    def fromArticleUpdate(update: ArticleUpdate) -> 'Article':
        _content = update.content
        _groups = update.groups
        _contentId = ContentID.getContentID(_content)
        _articleId = ArticleID.getArticleID(update)
        _title = update.title
        if (update.editOf is None):
            return Article(
                _title,
                _articleId,
                _contentId,
                _groups,
            )
        return Article(
            _title,
            _articleId,
            _contentId,
            _groups,
            update.editOf
        )


class ArticleRepository(ABC):
    _content: ContentRepository
    _history: HistoryRepository
    _groups: GroupRepository

    @property
    def groups(self) -> GroupRepository:
        return self._groups

    @property
    def content(self) -> ContentRepository:
        return self._content

    @abstractmethod
    def add_article(self, update: ArticleUpdate) -> Article:
        raise NotImplementedError

    @abstractmethod
    def update_article(self, update: ArticleUpdate) -> Article:
        raise NotImplementedError

    @abstractmethod
    def get_article(self, articleId: ArticleID) -> Article:
        raise NotImplementedError

    @abstractmethod
    def has_article(self, articleId: ArticleID | None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_articleIds(self) -> set[ArticleID]:
        raise NotImplementedError

    @abstractmethod
    def get_update(self, articleId: ArticleID) -> ArticleUpdate:
        raise NotImplementedError

    def merge_article(self, update: ArticleUpdate) -> Article:
        if (self.has_article(update.editOf)):
            return self.update_article(update)
        return self.add_article(update)


class MemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._articles: dict[ArticleID, Article] = {}
        self._content = MemoryContentRepository()
        self._history = MemoryHistoryRepository()
        self._groups = MemoryGroupRepository()

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
        return set(self._articles)

    def get_update(self, articleId: ArticleID) -> ArticleUpdate:
        _article = self._articles[articleId]
        _content = self._content.get_content(_article.contentId)
        return ArticleUpdate(
            _article.title,
            _content,
            _article.groups,
            _article.editOf
        )


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, paths: dict[str, Path]):
        if (not paths['articles'].exists()):
            raise FileNotFoundError(
                f'Articles folder not found in repository. The folder might not be initialized.')

        self._articles = paths['articles']
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
    def initialize_directory(cls, path: Path) -> dict[str, Path]:
        if (not path.exists()):
            raise FileNotFoundError
        path_is_not_empty = any(path.iterdir())
        if (path_is_not_empty):
            raise FileExistsError
        _articlePath = path.joinpath('articles')
        _articlePath.mkdir()
        FileSystemContentRepository.initialize_directory(path)
        FileSystemHistoryRepository.initialize_directory(path)
        FileSystemGroupRepository.initialize_directory(path)
        return cls.get_paths(path)

    def _add_article(self, update: ArticleUpdate) -> Article:
        _content = update.content
        _groups = update.groups
        _contentId = self._content.add_content(_content)
        _articleId = ArticleID.getArticleID(update)

        for group in _groups:
            self._groups.add_to_group(_contentId, group)

        return Article(
            update.title,
            _articleId,
            _contentId,
            _groups
        )

    def _write_article(self, article: Article) -> None:
        with self._articles.joinpath(article.articleId).open('wb') as _path:
            pickle.dump(article, _path)

    def _load_article(self, articleId: ArticleID) -> Article:
        with self._articles.joinpath(articleId).open('rb') as _path:
            _pickle = pickle.load(_path)
            return _pickle

    def add_article(self, update: ArticleUpdate) -> Article:
        newArticle = self._add_article(update)
        self._write_article(newArticle)
        return newArticle

    def get_article(self, articleId: ArticleID) -> Article:
        if (self.has_article(articleId)):
            return self._load_article(articleId)
        raise KeyError(
            'Article not found. Try using merge_article or add_article first.')

    def has_article(self, articleId: ArticleID | None) -> bool:
        if (articleId is None):
            return False
        return self._articles.joinpath(articleId).exists()

    def update_article(self, update: ArticleUpdate) -> Article:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError(
                'Article must be an edit of another Article already in the Repository. Try using merge_article or add_article instead.')

        newArticle = self._add_article(update)
        newArticle.editOf = update.editOf
        self._history.add_edit(newArticle.editOf, newArticle.articleId)
        self._write_article(newArticle)

        return newArticle

    def get_articleIds(self) -> set[ArticleID]:
        return {ArticleID(_article.name) for _article in self._articles.iterdir() if ArticleID.isValidID(_article.name)}

    def get_update(self, articleId: ArticleID) -> ArticleUpdate:
        _article = self.get_article(articleId)
        _content = self._content.get_content(_article.contentId)
        return ArticleUpdate(
            _article.title,
            _content,
            _article.groups,
            _article.editOf
        )
