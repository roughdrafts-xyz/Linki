
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator
from sigili.article.repository import Article, ArticleUpdate

from sigili.type.id import ArticleID, ContentID, DraftID, SourceID


@dataclass
class Draft:
    source: Article
    content: bytes
    contentId: ContentID
    groups: list[str]

    def asArticleUpdate(self) -> ArticleUpdate:
        return ArticleUpdate(
            self.source.title,
            self.content,
            self.groups,
            self.source.articleId
        )

    def should_update(self) -> bool:
        groups_different = self.groups != self.source.groups
        content_different = self.contentId != self.source.contentId
        return groups_different or content_different


class DraftRepository(ABC):
    @abstractmethod
    def set_draft(self, draft: Draft) -> Draft:
        raise NotImplementedError

    @abstractmethod
    def get_draft(self, articleId: ArticleID) -> Draft | None:
        raise NotImplementedError

    @abstractmethod
    def get_drafts(self) -> Iterator[Draft]:
        raise NotImplementedError

    @abstractmethod
    def clear_draft(self, articleId: ArticleID) -> None:
        raise NotImplementedError


class MemoryDraftRepository(DraftRepository):
    def __init__(self) -> None:
        self.drafts: dict[ArticleID, Draft] = dict()

    def set_draft(self, draft: Draft) -> Draft:
        articleId = draft.source.articleId
        self.drafts[articleId] = draft
        return draft

    def get_draft(self, articleId: ArticleID) -> Draft | None:
        return self.drafts.get(articleId, None)

    def get_drafts(self) -> Iterator[Draft]:
        return self.drafts.values().__iter__()

    def clear_draft(self, articleId: ArticleID) -> None:
        if (articleId in self.drafts):
            del self.drafts[articleId]
