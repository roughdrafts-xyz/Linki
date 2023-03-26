
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
    def get_source(self, sourceId: SourceID) -> Source:
        pass

    @abstractmethod
    def update_source(self, sourceId: SourceID, article: ArticleDetails) -> Source:
        pass

    @abstractmethod
    def should_update(self, draft: Draft) -> bool:
        pass
