
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sigili.article.repository import Article
from sigili.draft.repository import Draft
from sigili.type.id import ArticleID, ContentID, SourceID


@dataclass
class Source:
    sourceId: SourceID
    articleId: ArticleID
    contentId: ContentID
    groups: list[str]


class SourceRepository(ABC):
    @abstractmethod
    def set_source(self, sourceId: SourceID, article: Article) -> Source:
        pass

    @abstractmethod
    def get_source(self, sourceId: SourceID) -> Source | None:
        pass

    @abstractmethod
    def should_update(self, draft: Draft) -> bool:
        pass


class MemorySourceRepository(SourceRepository):
    def __init__(self) -> None:
        self.sources: dict[SourceID, Source] = dict()

    def set_source(self, sourceId: SourceID, article: Article) -> Source:
        source = Source(sourceId, article.articleId,
                        article.contentId, article.groups)
        self.sources[sourceId] = source
        return source

    def get_source(self, sourceId: SourceID) -> Source | None:
        return self.sources.get(sourceId, None)

    def should_update(self, draft: Draft) -> bool:
        source = self.get_source(draft.sourceId)
        if (source is None):
            return True

        groups_differ = (draft.groups != source.groups)
        content_differs = (draft.contentId != source.contentId)
        return groups_differ or content_differs
