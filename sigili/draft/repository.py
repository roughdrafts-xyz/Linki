
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sigili.type.id import DraftID, SourceID


@dataclass
class Draft:
    draftId: DraftID
    sourceId: SourceID


@dataclass
class DraftUpdate:
    sourceId: SourceID


class DraftRepository(ABC):
    @abstractmethod
    def add_draft(self, draft: Draft) -> Draft:
        raise NotImplementedError

    @abstractmethod
    def get_draft(self, draftId: DraftID) -> Draft | None:
        raise NotImplementedError

    @abstractmethod
    def update_draft(self, draftId: DraftID, update: DraftUpdate) -> Draft:
        raise NotImplementedError


class MemoryDraftRepository(DraftRepository):
    def __init__(self) -> None:
        self.drafts: dict[DraftID, Draft] = dict()

    def add_draft(self, draft: Draft) -> Draft:
        sourceId = draft.sourceId
        draftId = draft.draftId
        self.drafts[draftId] = Draft(draftId, sourceId)
        return draft

    def get_draft(self, draftId: DraftID) -> Draft | None:
        return self.drafts.get(draftId, None)

    def update_draft(self, draftId: DraftID, update: DraftUpdate) -> Draft:
        return self.add_draft(Draft(
            draftId,
            update.sourceId
        ))
