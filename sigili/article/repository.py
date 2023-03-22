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


@dataclass
class ArticleDetails():
    articleId: str


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


class MemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._articles = []
        self._content = MemoryContentRepository()
        self._history = MemoryHistoryRepository()
        self._groups = MemoryGroupRepository()

    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        _content = update.content
        _groups = update.groups

        _contentId = self._content.add_content(_content)
        for group in _groups:
            self._groups.add_to_group(_contentId, group)

        return ArticleDetails(
            articleId=_contentId
        )

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        return super().update_article(update)

    def merge_article(self, update: ArticleUpdate) -> ArticleDetails:
        return super().merge_article(update)


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, path: Path) -> None:
        super().__init__()

    @staticmethod
    def initialize_directory(path: Path) -> Path:
        return path
