from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


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


class BadArticleRepository(ArticleRepository):
    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        del update
        return ArticleDetails('')

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        del update
        return ArticleDetails('')

    def merge_article(self, update: ArticleUpdate) -> ArticleDetails:
        del update
        return ArticleDetails('')


class MemoryArticleRepository(ArticleRepository):
    pass


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, path: Path) -> None:
        super().__init__()

    @staticmethod
    def initialize_directory(path: Path) -> Path:
        return path
