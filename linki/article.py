from functools import cached_property
import pickle
from typing import Iterator

import msgspec
from linki.connection import Connection

from linki.id import ArticleID, BaseLabel


class BaseArticle(msgspec.Struct, dict=True, frozen=True, kw_only=True):
    label: BaseLabel
    content: str
    editOf: 'BaseArticle | None'
    redirect: BaseLabel | None = None

    @cached_property
    def articleId(self) -> ArticleID:
        return ArticleID.getArticleID(
            self.label, self.content, self.editOf)

    @classmethod
    def fromStream(cls, stream: bytes):
        res = pickle.loads(stream)
        return res

    def should_update(self) -> bool:
        if (self.editOf is None):
            return True
        label_different = self.label != self.editOf.label
        content_different = self.content != self.editOf.content
        return label_different or content_different


def Article(
    label: BaseLabel,
    content: str,
    editOf: BaseArticle | None
) -> BaseArticle:
    return BaseArticle(
        label=label,
        content=content,
        editOf=editOf
    )


class ArticleCollection():
    def __init__(self, connection: Connection[BaseArticle]) -> None:
        self.store = connection

    def merge_article(self, article: BaseArticle) -> BaseArticle:
        self.store[article.articleId] = article
        return article

    def get_article(self, articleId: ArticleID) -> BaseArticle | None:
        return self.store.get(articleId)

    def get_articles(self) -> Iterator[BaseArticle]:
        for article in self.store.values():
            yield article

    @classmethod
    def fromStream(cls, stream: bytes):
        res = pickle.loads(stream)
        return ArticleCollection(res)

    def __hash__(self) -> int:
        return hash(self.store)

    def __eq__(self, __value: object) -> bool:
        if (not isinstance(__value, ArticleCollection)):
            return False

        return self.store == __value.store
