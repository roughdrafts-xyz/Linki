from dataclasses import dataclass
from functools import cached_property
from typing import Iterator
from typing_extensions import Self

from linki.id import ArticleID, Label, SimpleLabel


@dataclass
class Article():
    label: Label
    content: str
    editOf: Self | None

    @cached_property
    def articleId(self) -> ArticleID:
        return ArticleID.getArticleID(
            self.label, self.content, self.editOf)


@dataclass
class SimpleArticle(Article):
    label: SimpleLabel

    def __init__(self, name: str, content: str, editOf: Article | None) -> None:
        self.label = SimpleLabel(name)
        self.content = content
        self.editOf = editOf


class ArticleCollection():
    def __init__(self, connection) -> None:
        self.articles = connection

    def merge_article(self, article: SimpleArticle | None) -> SimpleArticle | None:
        if (article is None):
            return None
        self.articles[article.articleId] = article
        return article

    def get_article(self, articleId: ArticleID) -> SimpleArticle | None:
        if (self.has_article(articleId)):
            return self.articles[articleId]
        return None

    def get_articles(self) -> Iterator[ArticleID]:
        for key in self.articles.keys():
            yield ArticleID(key)

    def has_article(self, articleId: ArticleID | None) -> bool:
        return articleId in self.articles
