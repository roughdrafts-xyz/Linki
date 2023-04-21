import pickle
from typing import Iterator
from linki.article import Article
from linki.connection import Connection

from linki.id import BaseLabel


class Title(Article):
    editOf: Article | None
    redirect: BaseLabel | None = None

    @classmethod
    def fromArticle(cls, article: Article) -> 'Title':
        return cls(
            article.label,
            article.content,
            article.editOf
        )

    @classmethod
    def createRedirect(cls, editOf: Article, redirect: BaseLabel) -> 'Title':
        path_string = ','.join(redirect.path)
        content = f'[redirect:{path_string}#{redirect.labelId}]'
        title = cls(
            label=editOf.label,
            content=content,
            editOf=editOf,
        )
        title.redirect = redirect
        return title


class TitleCollection():
    def __init__(self, connection: Connection[Title]) -> None:
        self.titles = connection

    def set_title(self, title: Title | Article) -> Title:
        if (not isinstance(title, Title)):
            title = Title.fromArticle(title)
        self.titles[title.label.labelId] = title
        return title

    def get_title(self, title: BaseLabel) -> Title | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def get_titles(self) -> Iterator[Title]:
        for item in self.titles.values():
            yield item

    def clear_title(self, title: BaseLabel) -> None:
        if (title.labelId in self.titles):
            del self.titles[title.labelId]

    @classmethod
    def fromStream(cls, stream: bytes):
        res = pickle.loads(stream)
        return TitleCollection(res)

    def __hash__(self) -> int:
        return hash(self.titles)

    def __eq__(self, __value: object) -> bool:
        if (not isinstance(__value, TitleCollection)):
            return False

        return self.titles == __value.titles
