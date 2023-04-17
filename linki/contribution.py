from abc import ABC
from dataclasses import dataclass
from typing import Iterator
from urllib.parse import urlparse
from linki.connection import Connection
from linki.draft import Draft
from linki.title import TitleCollection
from linki.id import LabelID


@dataclass
class Contribution():
    titles: TitleCollection
    remote: TitleCollection

    def announce_updates(self) -> Iterator[Draft]:
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
