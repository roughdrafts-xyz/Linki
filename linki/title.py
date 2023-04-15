from dataclasses import dataclass
from typing import Iterator
from linki.article import Article
from linki.connection import Connection

from linki.id import Label


@dataclass
class Title():
    label: Label
    article: Article

    @classmethod
    def fromArticle(cls, article: Article) -> 'Title':
        return cls(
            article.label,
            article
        )


class TitleCollection():
    def __init__(self, connection: Connection[Title]) -> None:
        self.titles = connection

    def set_title(self, article: Article) -> Title | None:
        title = Title.fromArticle(article)
        self.titles[title.label.labelId] = title
        return title

    def get_title(self, title: Label) -> Title | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def get_titles(self) -> Iterator[Title]:
        return self.titles.values().__iter__()

    def clear_title(self, title: Label) -> None:
        if (title.labelId in self.titles):
            del self.titles[title.labelId]
