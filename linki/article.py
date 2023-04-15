from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from typing_extensions import Self
from urllib.parse import urlparse

from linki.connection import Connection, MemoryConnection, PathConnection
from linki.id import ID, ArticleID, Label


@dataclass
class Article():
    articleId: ArticleID
    label: Label
    content: bytes
    editOf: Self | None

    def __init__(self, label: str, content: bytes, editOf: Self | None = None) -> None:
        self.label = Label(label)
        self.content = content
        self.editOf = editOf
        self.articleId = ArticleID.getArticleID(
            self.label, self.content, self.editOf)


class ArticleCollection():
    def __init__(self, connection: Connection[Article]) -> None:
        self.articles = connection

    def merge_article(self, article: Article) -> Article:
        self.articles[article.articleId] = article
        return article

    def get_article(self, articleId: ArticleID) -> Article:
        if (self.has_article(articleId)):
            return self.articles[articleId]
        raise KeyError(
            'Article not found. Try using merge_article or add_article first.')

    def get_articles(self) -> Iterator[ArticleID]:
        for key in self.articles.keys():
            yield ArticleID(key)

    def has_article(self, articleId: ArticleID | None) -> bool:
        return articleId in self.articles
