
from dataclasses import dataclass
from linki.connection import Connection

from linki.id import BaseLabel, Label
from linki.url import URL


@dataclass
class Change():
    size: int
    label: BaseLabel
    change_label: BaseLabel

    @property
    def change_id(self) -> str:
        return self.change_label.labelId[0:7]

    @property
    def path(self) -> str:
        return '/'.join(self.label.path)


def ChangeLabel(base: str, path: str):
    return Label([base, path])


class ChangeCollection():
    def __init__(self, connection: Connection[Change]) -> None:
        self.store = connection

    def add_change(self, change: Change):
        self.store[change.change_label.labelId] = change

    def get_changes(self, url: URL | None = None):
        for change_id in self.store:
            change = self.store[change_id]
            if (url is None):
                yield change
                continue

            inbox_label = ChangeLabel(url.url, '/'.join(change.label.path))
            if (inbox_label == change.change_label):
                yield change
