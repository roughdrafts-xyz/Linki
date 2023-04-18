from dataclasses import dataclass
from typing import Iterator
from linki.article import SimpleArticle

from linki.id import SimpleLabel


@dataclass
class Title():
    label: SimpleLabel
    article: SimpleArticle

    @classmethod
    def fromArticle(cls, article: SimpleArticle) -> 'Title':
        return cls(
            article.label,
            article
        )


class TitleCollection():
    def __init__(self, connection) -> None:
        self.titles = connection

    def set_title(self, article: SimpleArticle | None) -> Title | None:
        if (article is None):
            return None
        title = Title.fromArticle(article)
        self.titles[title.label.labelId] = title
        return title

    def get_title(self, title: SimpleLabel) -> Title | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def get_titles(self) -> Iterator[Title]:
        return self.titles.values().__iter__()

    def clear_title(self, title: SimpleLabel) -> None:
        if (title.labelId in self.titles):
            del self.titles[title.labelId]
