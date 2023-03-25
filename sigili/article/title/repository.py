from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TitleDetails:
    title: str
    articleId: str


class TitleRepository(ABC):
    @abstractmethod
    def set_title(self, title: str, articleId: str | None) -> TitleDetails | None:
        raise NotImplementedError

    @abstractmethod
    def get_title(self, title) -> TitleDetails:
        raise NotImplementedError

    @abstractmethod
    def get_titles(self) -> list[TitleDetails]:
        raise NotImplementedError

    @abstractmethod
    def get_options(self, title) -> list[TitleDetails]:
        raise NotImplementedError


class MemoryTitleRepository():
    def __init__(self) -> None:
        self.titles: dict[str, TitleDetails] = dict()
        self.store: dict[str, list[TitleDetails]] = dict()

    def set_title(self, title: str, articleId: str | None) -> TitleDetails | None:
        if (articleId is None):
            del self.titles[title]
            return None

        _title_detail = TitleDetails(
            title,
            articleId
        )

        if (title not in self.store):
            self.store[title] = []
        self.store[title].append(_title_detail)
        self.titles[title] = _title_detail
        return _title_detail

    def get_title(self, title) -> TitleDetails:
        return self.titles[title]

    def get_titles(self) -> list[TitleDetails]:
        return list(self.titles.values())

    def get_options(self, title) -> list[TitleDetails]:
        return list(self.store[title])
