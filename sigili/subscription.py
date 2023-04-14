from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse
from sigili.connection import Connection, MemoryConnection, PathConnection
from sigili.draft.repository import Draft, MemoryDraftRepository
from sigili.title.repository import TitleRepository
from sigili.type.id import ID, Label, LabelID


@dataclass
class SubscriptionURL():
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


class Updater():
    def __init__(self, titles: TitleRepository, remote: TitleRepository) -> None:
        drafts = MemoryDraftRepository()
        for title in remote.get_titles():
            current = titles.get_title(title.label)
            editOf = None
            if (current is not None):
                editOf = current.article
            draft = Draft(
                title.label,
                title.article.content,
                editOf
            )
            drafts.set_draft(draft)


@dataclass
class Update():
    labelId: LabelID
    url: SubscriptionURL
    size: int


class SubscriptionRepository(ABC):
    subscriptions: Connection[SubscriptionURL]

    def add_subscription(self, url: str):
        SubURL = SubscriptionURL(url)
        self.subscriptions[SubURL.labelId] = SubURL

    def get_subscription(self, label: str):
        _id = LabelID(label)
        return self.subscriptions.get(_id)

    def get_subscriptions(self) -> Iterator[ID]:
        return self.subscriptions.__iter__()

    def get_updates(self, titles: TitleRepository):
        # TODO Optimize. No one likes this many loops.

        for sub in self.get_subscriptions():
            label = Label('')
            yield Update(label.labelId, SubscriptionURL('file://dev/null/'), 0)
            # start an editor using local articles and titles
            # load remote titles as drafts
            # dry publish and report changes


class MemorySubscriptionRepository(SubscriptionRepository):
    def __init__(self) -> None:
        self.subscriptions = MemoryConnection[SubscriptionURL]()


class PathSubscriptionRepository(SubscriptionRepository):
    def __init__(self, path: Path) -> None:
        self.subscriptions = PathConnection[SubscriptionURL](path.resolve())

    @staticmethod
    def init(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _titlePath = path.joinpath('subscriptions')
        _titlePath.mkdir()
        return _titlePath.resolve()
