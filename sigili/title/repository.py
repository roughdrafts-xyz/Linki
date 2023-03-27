from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator
from sigili.article.repository import Article, ArticleRepository, ArticleUpdate

from sigili.type.id import ArticleID, Title


class TitleRepository(ABC):
    articles: ArticleRepository

    @abstractmethod
    def set_title(self, title: str, update: ArticleUpdate) -> Article:
        raise NotImplementedError

    @abstractmethod
    def get_title(self, title) -> Article:
        raise NotImplementedError

    @abstractmethod
    def clear_title(self, title: Title) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_titles(self) -> Iterator[Article]:
        raise NotImplementedError

    def get_options(self, title: Title) -> Iterator[Article]:
        for articleId in self.articles.get_articleIds():
            article = self.articles.get_article(articleId)
            if (article.title == title):
                yield article


class MemoryTitleRepository(TitleRepository):
    def __init__(self, articles: ArticleRepository) -> None:
        self.titles: dict[Title, Article] = dict()
        self.articles = articles

    def set_title(self, title: Title, update: ArticleUpdate) -> Article:
        article = self.articles.add_article(update)
        self.titles[title] = article
        return article

    def get_title(self, title) -> Article:
        return self.titles[title]

    def clear_title(self, title: Title) -> None:
        if (title in self.titles):
            del self.titles[title]

    def get_titles(self) -> Iterator[Article]:
        return self.titles.values().__iter__()
