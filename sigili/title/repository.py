from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from urllib.parse import urlparse
from sigili.article.repository import Article
from sigili.connection import Connection, MemoryConnection, PathConnection

from sigili.type.id import Label


@dataclass
class Title():
    label: Label
    article: Article

    @classmethod
    def fromArticle(cls, article: Article) -> 'Title':
        return cls(
            article.label,
            article
        )


class TitleRepository(ABC):
    titles: Connection[Title]

    def set_title(self, article: Article) -> Title | None:
        title = Title.fromArticle(article)
        self.titles[title.label.labelId] = title
        return title

    def get_title(self, title: Label) -> Title | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def get_titles(self) -> Iterator[Title]:
        return self.titles.values().__iter__()

    def clear_title(self, title: Label) -> None:
        if (title.labelId in self.titles):
            del self.titles[title.labelId]

    @staticmethod
    def fromURL(url: str | None = None):
        if (url is None):
            return MemoryTitleRepository()
        _url = urlparse(url)
        match _url.scheme:
            case 'file':
                return FileSystemTitleRepository(Path(_url.path))
            case 'ssh':
                raise NotImplementedError
            case 'http':
                raise NotImplementedError
            case _:
                raise NotImplementedError


class MemoryTitleRepository(TitleRepository):
    def __init__(self) -> None:
        self.titles = MemoryConnection[Title]()


class FileSystemTitleRepository(TitleRepository):
    def __init__(self, path: Path) -> None:
        self.titles = PathConnection[Title](path.resolve())

    @staticmethod
    def init(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _titlePath = path.joinpath('titles')
        _titlePath.mkdir()
        return _titlePath.resolve()
