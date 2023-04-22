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
        self.store = connection

    def set_title(self, title: BaseArticle | BaseArticle) -> BaseArticle:
        self.store[title.label.labelId] = title
        return title

    def get_title(self, title: BaseLabel) -> BaseArticle | None:
        if (title.labelId not in self.store):
            return None
        return self.store[title.labelId]

    def get_titles(self) -> Iterator[BaseArticle]:
        for item in self.store.values():
            yield item

    def clear_title(self, title: BaseLabel) -> None:
        if (title.labelId in self.store):
            del self.store[title.labelId]

    @classmethod
    def fromStream(cls, stream: bytes):
        res = pickle.loads(stream)
        return TitleCollection(res)

    def __hash__(self) -> int:
        return hash(self.store)

    def __eq__(self, __value: object) -> bool:
        if (not isinstance(__value, TitleCollection)):
            return False

        return self.store == __value.store
