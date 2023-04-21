from dataclasses import dataclass
from typing import Iterator
from linki.article import Article
from linki.connection import Connection

from linki.id import Label


@dataclass
class Title(Article):
    editOf: Article | None = None
    redirect: Label | None = None

    @classmethod
    def fromArticle(cls, article: Article) -> 'Title':
        return cls(
            article.label,
            article.content,
            article.editOf
        )

    @classmethod
    def createRedirect(cls, editOf: Article, redirect: Label) -> 'Title':
        path_string = ','.join(redirect.path)
        content = f'[redirect:{path_string}#{redirect.labelId}]'
        return cls(
            label=editOf.label,
            content=content,
            editOf=editOf,
            redirect=redirect
        )

    def __hash__(self) -> int:
        return super().__hash__()


class TitleCollection():
    def __init__(self, connection: Connection[Title]) -> None:
        self.titles = connection

    def set_title(self, title: Title | Article) -> Title:
        if (not isinstance(title, Title)):
            title = Title.fromArticle(title)
        self.titles[title.label.labelId] = title
        return title

    def get_title(self, title: Label) -> Title | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def get_titles(self) -> Iterator[Title]:
        for item in self.titles.values():
            yield item

    def clear_title(self, title: Label) -> None:
        if (title.labelId in self.titles):
            del self.titles[title.labelId]
