from dataclasses import asdict, dataclass
from typing import Iterator, cast
from linki.article import Article
from linki.connection import Connection

from linki.id import Label


@dataclass
class Title(Article):
    redirect: Label | None = None
    editOf: Article | None = None

    @classmethod
    def fromArticle(cls, article: Article) -> 'Title':
        return cls(
            article.label,
            article.content,
            article.editOf
        )


class Redirect(Title):
    redirect: Label
    editOf: Title

    def __init__(self, editOf: Title, redirect: Label):
        self.redirect = redirect
        self.editOf = editOf

    @property
    def content(self) -> str:
        path_string = ','.join(self.redirect.path)
        return f'[redirect:{path_string}#{self.redirect.labelId}]'

    @property
    def label(self) -> Label:
        return self.editOf.label


class TitleCollection():
    def __init__(self, connection: Connection[Title]) -> None:
        self.titles = connection

    def set_title(self, article: Article) -> Title:
        title = Title.fromArticle(article)
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
