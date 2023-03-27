
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator
from sigili.article.repository import Article, ArticleUpdate

from sigili.type.id import ArticleID, BlankArticleID, ContentID, Title


@dataclass
class Draft:
    title: Title
    content: bytes
    groups: list[str]
    editOf: Article | None = None

    def should_update(self) -> bool:
        if (self.editOf is None):
            return True
        if (self.contentId is None):
            self.contentId = ContentID.getContentID(self.content)
        groups_different = self.groups != self.editOf.groups
        content_different = self.contentId != self.editOf.contentId
        return groups_different or content_different

    def asArticleUpdate(self):
        if (self.editOf is None):
            return ArticleUpdate(
                self.title,
                self.content,
                self.groups,
            )
        return ArticleUpdate(
            self.title,
            self.content,
            self.groups,
            self.editOf.articleId
        )


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
        self.drafts: dict[Title, Draft] = dict()

    def set_draft(self, draft: Draft) -> Draft:
        self.drafts[draft.title] = draft
        return draft

    def get_draft(self, articleId: ArticleID) -> Draft | None:
        return self.drafts.get(articleId, None)

    def get_drafts(self) -> Iterator[Draft]:
        return self.drafts.values().__iter__()

    def clear_draft(self, articleId: ArticleID) -> None:
        if (articleId in self.drafts):
            del self.drafts[articleId]
