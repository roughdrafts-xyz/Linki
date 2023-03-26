
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sigili.type.id import ContentID, DraftID, SourceID


@dataclass
class Draft:
    sourceId: SourceID
    contentId: ContentID
    groups: list[str]


class DraftRepository(ABC):
    @abstractmethod
    def set_draft(self, draft: Draft) -> Draft:
        raise NotImplementedError

    @abstractmethod
    def get_draft(self, draftId: DraftID) -> Draft | None:
        raise NotImplementedError


class MemoryDraftRepository(DraftRepository):
    def __init__(self) -> None:
        self.drafts: dict[SourceID, Draft] = dict()

    def set_draft(self, draft: Draft) -> Draft:
        sourceId = draft.sourceId
        self.drafts[sourceId] = draft
        return draft

    def get_draft(self, sourceId: SourceID) -> Draft | None:
        return self.drafts.get(sourceId, None)
