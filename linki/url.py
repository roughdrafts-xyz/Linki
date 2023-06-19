from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse

from linki.connection import Connection

from linki.id import LabelID, SimpleLabel


@dataclass
class URL():
    valid_schemes = ['file', 'https']

    def __init__(self, url: str) -> None:
        self.url = url
        if (not self.is_valid_url(self.url)):
            path = Path(self.url)
            if (path.exists()):
                self.url = path.resolve().as_uri()

        if (not self.is_valid_url(self.url)):
            valid_schemes = ', '.join(self.valid_schemes)
            raise ValueError(
                f'Invalid URL. Must be one of these schemes: {valid_schemes}')

        self.parsed = urlparse(self.url)
        self.labelId = SimpleLabel(self.url).labelId

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
        self.store = connection

    def add_url(self, url: str):
        new_url = URL(url)
        self.store[new_url.labelId] = new_url
        return new_url

    def get_url(self, label: str):
        _id = LabelID(label)
        return self.store.get(_id)

    def get_urls(self) -> Iterator[URL]:
        for url in self.store.values():
            yield url

    def render_urls(self) -> str:
        priority = 0
        output = f'{priority}\tThis Wiki'
        for url in self.get_urls():
            priority += 1
            output += f"\n{priority}\t{url.url}"
        return output
