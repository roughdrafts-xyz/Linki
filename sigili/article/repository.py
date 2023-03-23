from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from sigili.article.content.repository import MemoryContentRepository
from sigili.article.group.repository import MemoryGroupRepository
from sigili.article.history.repository import MemoryHistoryRepository


@dataclass
class ArticleUpdate():
    content: bytes
    groups: list[str]
    editOf: str | None = None


@dataclass
class ArticleDetails():
    articleId: str
    groups: list[str]
    editOf: str | None = None


class ArticleRepository(ABC):
    @abstractmethod
    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        raise NotImplementedError

    @abstractmethod
    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        raise NotImplementedError

    @abstractmethod
    def merge_article(self, update: ArticleUpdate) -> ArticleDetails:
        raise NotImplementedError

    @abstractmethod
    def get_article(self, articleId: str) -> ArticleDetails:
        raise NotImplementedError

    @abstractmethod
    def has_article(self, articleId: str | None) -> bool:
        raise NotImplementedError


class MemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._articles = {}
        self._content = MemoryContentRepository()
        self._history = MemoryHistoryRepository()
        self._groups = MemoryGroupRepository()

    def _add_article(self, update: ArticleUpdate) -> ArticleDetails:
        _content = update.content
        _groups = update.groups

        _contentId = self._content.add_content(_content)
        for group in _groups:
            self._groups.add_to_group(_contentId, group)

        return ArticleDetails(
            articleId=_contentId,
            groups=_groups
        )

    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        newArticle = self._add_article(update)
        self._articles[newArticle.articleId] = newArticle
        return newArticle

    def get_article(self, articleId: str) -> ArticleDetails:
        if (self.has_article(articleId)):
            return self._articles[articleId]
        raise KeyError(
            'Article not found. Try using merge_article or add_article first.')

    def has_article(self, articleId: str | None) -> bool:
        return articleId in self._articles

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError(
                'Article must be an edit of another Article already in the Repository. Try using merge_article or add_article instead.')

        newArticle = self._add_article(update)
        newArticle.editOf = update.editOf
        self._history.add_edit(newArticle.editOf, newArticle.articleId)
        self._articles[newArticle.articleId] = newArticle

        return newArticle

    def merge_article(self, update: ArticleUpdate) -> ArticleDetails:
        if (self.has_article(update.editOf)):
            return self.update_article(update)
        return self.add_article(update)


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, path: Path) -> None:
        super().__init__()

    @staticmethod
    def initialize_directory(path: Path) -> Path:
        return path
