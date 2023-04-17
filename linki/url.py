from dataclasses import dataclass
from typing import Iterator
from urllib.parse import urlparse
from linki.connection import Connection

from linki.id import LabelID


@dataclass
class URL():
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


class URLCollection():
    def __init__(self, connection: Connection[URL]) -> None:
        self.subscriptions = connection

    def add_url(self, url: str):
        subURL = URL(url)
        self.subscriptions[subURL.labelId] = subURL

    def get_url(self, label: str):
        _id = LabelID(label)
        return self.subscriptions.get(_id)

    def get_urls(self) -> Iterator[URL]:
        for url in self.subscriptions.values():
            yield url
