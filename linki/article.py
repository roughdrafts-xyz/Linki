from dataclasses import dataclass
from typing import Iterator
from typing_extensions import Self

from linki.id import ArticleID, SimpleLabel


@dataclass
class Article():
    articleId: ArticleID
    label: SimpleLabel
    content: str
    editOf: Self | None

    def __init__(self, label: str, content: str, editOf: Self | None = None) -> None:
        self.label = SimpleLabel(label)
        self.content = content
        self.editOf = editOf
        self.articleId = ArticleID.getArticleID(
            self.label, self.content, self.editOf)


class ArticleCollection():
    def __init__(self, connection) -> None:
        self.articles = connection

    def merge_article(self, article: Article | None) -> Article | None:
        if (article is None):
            return None
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
