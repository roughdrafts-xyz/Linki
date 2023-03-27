from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import string
from typing import Iterator
from sigili.article.repository import Article, ArticleRepository, ArticleUpdate

from sigili.type.id import ArticleID, Label, LabelID


class Title(Article):
    pass


class TitleRepository(ABC):
    articles: ArticleRepository

    @abstractmethod
    def set_title(self, title: Label, update: ArticleUpdate) -> Article | None:
        raise NotImplementedError

    @abstractmethod
    def get_title(self, title) -> Article | None:
        raise NotImplementedError

    @abstractmethod
    def clear_title(self, title: Label) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_titles(self) -> Iterator[Article]:
        raise NotImplementedError

    def get_options(self, title: Label) -> Iterator[Article]:
        for articleId in self.articles.get_articleIds():
            article = self.articles.get_article(articleId)
            if (article.title == title):
                yield article


class MemoryTitleRepository(TitleRepository):
    def __init__(self, articles: ArticleRepository) -> None:
        self.titles: dict[LabelID, Article] = dict()
        self.articles = articles

    def set_title(self, title: Label, update: ArticleUpdate) -> Article | None:
        article = self.articles.add_article(update)
        self.titles[title.labelId] = article
        return article

    def get_title(self, title: Label) -> Article | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def clear_title(self, title: Label) -> None:
        if (title.labelId in self.titles):
            del self.titles[title.labelId]

    def get_titles(self) -> Iterator[Article]:
        return self.titles.values().__iter__()


class FileSystemTitleRepository(TitleRepository):
    def __init__(self, articles: ArticleRepository, path: Path) -> None:
        self._titles = path
        self.articles = articles

    @staticmethod
    def initialize_directory(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _titlePath = path.joinpath('titles')
        _titlePath.mkdir()
        return _titlePath.resolve()

    def set_title(self, title: Label, update: ArticleUpdate) -> Article | None:
        article = self.articles.add_article(update)
        self._titles.joinpath(title.labelId).write_text(article.articleId)
        return article

    def get_title(self, title: Label) -> Article | None:
        _title = self._titles.joinpath(title.labelId)
        if (not _title.exists()):
            return None
        _article = _title.read_text()
        article = self.articles.get_article(ArticleID(_article))
        return article

    def clear_title(self, title: Label) -> None:
        _title = self._titles.joinpath(title.labelId)
        if (not _title.exists()):
            return None
        _title.unlink()

    def get_titles(self) -> Iterator[Article]:
        for _title in self._titles.iterdir():
            article_id = ArticleID(_title.read_text())
            yield self.articles.get_article(article_id)
