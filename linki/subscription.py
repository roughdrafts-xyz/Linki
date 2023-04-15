from abc import ABC
from dataclasses import dataclass
from typing import Iterator
from urllib.parse import urlparse
from linki.connection import Connection
from linki.draft import Draft
from linki.title import TitleCollection
from linki.id import LabelID


@dataclass
class SubURL():
    valid_schemes = ['file', 'http']

    def __init__(self, url: str) -> None:
        if (not self.is_valid_url(url)):
            valid_schemes = ', '.join(self.valid_schemes)
            raise ValueError(
                f'Invalid URL. Must be one of these schemes: {valid_schemes}')
        self.url = url
        self.parsed = urlparse(url)
        self.labelId = LabelID.getLabelID(url)

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        parsed = urlparse(url)
        if (parsed.scheme not in cls.valid_schemes):
            return False
        if (len(parsed.path) <= 0):
            return False
        return True


class SubURLCollection(ABC):
    def __init__(self, connection: Connection[SubURL]) -> None:
        self.subscriptions = connection

    def add_sub_url(self, url: str):
        subURL = SubURL(url)
        self.subscriptions[subURL.labelId] = subURL

    def get_sub_url(self, label: str):
        _id = LabelID(label)
        return self.subscriptions.get(_id)

    def get_sub_urls(self) -> Iterator[SubURL]:
        for url in self.subscriptions.values():
            yield url


@dataclass
class Subscription():
    titles: TitleCollection
    remote: TitleCollection

    def get_updates(self) -> Iterator[Draft]:
        for title in self.remote.get_titles():
            current = self.titles.get_title(title.label)
            editOf = None
            if (current is not None):
                editOf = current.article
            draft = Draft(
                title.label,
                title.article.content,
                editOf
            )
            if (draft.should_update()):
                yield draft
