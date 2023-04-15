from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List
from urllib.parse import urlparse
from sigili.article.repository import Article
from sigili.connection import Connection, MemoryConnection, PathConnection
from sigili.draft.repository import Draft, MemoryDraftRepository
from sigili.repository import Repository, RepositoryConnection
from sigili.title import TitleCollection
from sigili.type.id import ID, ArticleID, Label, LabelID


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


@dataclass
class InboxRow():
    rowId: int
    url: SubURL
    label: Label
    size: int


class Inbox():
    def __init__(self, subs: SubURLCollection,  titles: TitleCollection) -> None:
        self.subs = subs
        self.titles = titles
        pass

    def get_inbox(self):
        # TODO Optimize. No one likes this many loops.
        count = 0
        for sub in self.subs.get_sub_urls():
            repo = Repository(sub.url)
            remote = repo.titles
            subscription = Subscription(self.titles, remote)
            for update in subscription.get_updates():
                size = len(update.content)
                if (update.editOf is not None):
                    size -= len(update.editOf.content)
                yield InboxRow(count, sub, update.label, size)
