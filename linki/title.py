import pickle
from typing import Iterator
from linki.article import BaseArticle
from linki.connection import Connection

from linki.id import BaseLabel


def Title(
    label: BaseLabel,
    content: str,
    editOf: BaseArticle | None
) -> BaseArticle:
    return BaseArticle(
        label=label,
        content=content,
        editOf=editOf
    )


def Redirect(editOf: BaseArticle, redirect: BaseLabel) -> 'BaseArticle':
    path_string = ','.join(redirect.path)
    content = f'[redirect:{path_string}#{redirect.labelId}]'
    return BaseArticle(
        label=editOf.label,
        content=content,
        editOf=editOf,
        redirect=redirect
    )


class TitleCollection():
    def __init__(self, connection: Connection[BaseArticle]) -> None:
        self.titles = connection

    def set_title(self, title: BaseArticle | BaseArticle) -> BaseArticle:
        self.titles[title.label.labelId] = title
        return title

    def get_title(self, title: BaseLabel) -> BaseArticle | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def get_titles(self) -> Iterator[BaseArticle]:
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
