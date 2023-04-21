from dataclasses import dataclass
from functools import cached_property
import pickle
from typing import Iterator
from linki.connection import Connection, MemoryConnection

from linki.id import ArticleID, Label


@dataclass
class Article():
    label: Label
    content: str
    editOf: 'Article | None'

    @cached_property
    def articleId(self) -> ArticleID:
        return ArticleID.getArticleID(
            self.label, self.content, self.editOf)

    @classmethod
    def fromStream(cls, stream: bytes):
        res = pickle.loads(stream)
        return res

    def __hash__(self) -> int:
        return hash(self.articleId)

    def __eq__(self, __value: object) -> bool:
        if (isinstance(__value, Article)):
            return self.articleId == __value.articleId
        return False


class ArticleCollection():
    def __init__(self, connection: Connection[Article]) -> None:
        self.articles = connection

    def merge_article(self, article: Article) -> Article:
        self.articles[article.articleId] = article
        return article

    def get_article(self, articleId: ArticleID) -> Article | None:
        if (self.has_article(articleId)):
            return self.articles[articleId]
        return None

    def get_articles(self) -> Iterator[ArticleID]:
        for key in self.articles.keys():
            yield ArticleID(key)

    def has_article(self, articleId: ArticleID | None) -> bool:
        return articleId in self.articles

    @classmethod
    def fromStream(cls, stream: bytes):
        res = pickle.loads(stream)
        articles = cls(MemoryConnection[Article]())
        for article in res:
            articles.merge_article(article)
        return articles

    def __hash__(self) -> int:
        return hash(self.articles)

    def __eq__(self, __value: object) -> bool:
        if (not isinstance(__value, ArticleCollection)):
            return False

        return self.articles == __value.articles
