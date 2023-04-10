from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from sigili.article.repository import ArticleRepository, FileSystemArticleRepository, MemoryArticleRepository
from sigili.connection import Connection, MemoryConnection, PathConnection
from sigili.title.repository import FileSystemTitleRepository, MemoryTitleRepository, TitleRepository
from sigili.type.id import ID, Label, LabelID


@dataclass
class Subscription:
    titles: TitleRepository
    articles: ArticleRepository

    @classmethod
    def fromPath(cls, path: Path):
        _path = path.joinpath('.sigili')
        titles = FileSystemTitleRepository(_path.joinpath('titles'))
        a_paths = FileSystemArticleRepository.get_paths(_path)
        articles = FileSystemArticleRepository(a_paths)
        return cls(titles, articles)


@dataclass
class SubscriptionURL(Label):
    def __init__(self, name: str) -> None:
        super().__init__(name)


class SubscriptionRepository():
    subscriptions: Connection[SubscriptionURL]

    def add_subscription(self, url: str):
        SubURL = SubscriptionURL(url)
        self.subscriptions[SubURL.labelId] = SubURL

    def get_subscriptions(self) -> Iterator[ID]:
        return self.subscriptions.__iter__()


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
