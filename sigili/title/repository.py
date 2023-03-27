from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator
from sigili.article.repository import Article, ArticleRepository

from sigili.type.id import ArticleID


class TitleRepository(ABC):
    articles: ArticleRepository

    @abstractmethod
    def set_title(self, title: str, article: Article | None) -> Article | None:
        raise NotImplementedError

    @abstractmethod
    def get_title(self, title) -> Article:
        raise NotImplementedError

    @abstractmethod
    def get_titles(self) -> Iterator[Article]:
        raise NotImplementedError

    def get_options(self, title) -> Iterator[Article]:
        for articleId in self.articles.get_articleIds():
            article = self.articles.get_article(articleId)
            if (article.title == title):
                yield article


class MemoryTitleRepository(TitleRepository):
    def __init__(self, articles: ArticleRepository) -> None:
        self.titles: dict[str, Article] = dict()
        self.articles = articles

    def set_title(self, title: str, article: Article | None) -> Article | None:
        if (article is None):
            del self.titles[title]
            return None
        self.titles[title] = article
        return article

    def get_title(self, title) -> Article:
        return self.titles[title]

    def get_titles(self) -> Iterator[Article]:
        return self.titles.values().__iter__()
