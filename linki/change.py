
from dataclasses import dataclass
from linki.article import BaseArticle
from linki.connection import Connection

from linki.id import LabelID, SimpleLabel
from linki.url import URL


@dataclass
class Change():
    article: BaseArticle
    url: URL
    changes: BaseArticle | None = None

    @property
    def label(self):
        return ChangeLabel(self.url, self.article)

    @property
    def change_id(self) -> str:
        return self.label.labelId[0:7]

    @property
    def path(self) -> str:
        return '/'.join(self.article.label.path)

    @property
    def size(self) -> int:
        size = len(self.article.content)
        if (self.changes is not None):
            size -= len(self.changes.content)
        return size


def ChangeLabel(base: URL, article: BaseArticle):
    path = '/'.join(article.label.path)
    return SimpleLabel(f'{base.url}{path}')


class ChangeCollection():
    def __init__(self, connection: Connection[Change]) -> None:
        self.store = connection

    def add_change(self, change: Change):
        self.store[change.label.labelId] = change

    def find_change_id(self, key: str):
        return [
            change_id for change_id in self.store
            if change_id.startswith(key)
        ]

    def get_change(self, change_id: str):
        return self.store.get(LabelID(change_id))

    def get_changes(self, url: URL | None = None):
        for change_id in self.store:
            change = self.store[change_id]
            if (url is None):
                yield change
                continue

            inbox_label = ChangeLabel(url, change.article)
            if (inbox_label == change.label):
                yield change
