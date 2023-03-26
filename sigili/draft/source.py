
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sigili.article.repository import ArticleDetails
from sigili.draft.repository import Draft
from sigili.type.id import ArticleID, SourceID


@dataclass
class Source:
    sourceId: SourceID
    articleId: ArticleID


class SourceRepository(ABC):
    @abstractmethod
    def add_source(self, sourceId: SourceID, article: ArticleDetails) -> Source:
        pass

    @abstractmethod
    def get_source(self, sourceId: SourceID) -> Source | None:
        pass

    @abstractmethod
    def update_source(self, sourceId: SourceID, article: ArticleDetails) -> Source:
        pass

    @abstractmethod
    def should_update(self, draft: Draft) -> bool:
        pass


class MemorySourceRepository(SourceRepository):
    def __init__(self) -> None:
        self.sources: dict[SourceID, Source] = dict()

    def add_source(self, sourceId: SourceID, article: ArticleDetails) -> Source:
        source = Source(sourceId, article.articleId)
        self.sources[sourceId] = source
        return source

    def get_source(self, sourceId: SourceID) -> Source | None:
        return self.sources.get(sourceId, None)

    def update_source(self, sourceId: SourceID, article: ArticleDetails) -> Source:
        return self.add_source(sourceId, article)

    def should_update(self, draft: Draft) -> bool:
        return False
