
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sigili.draft import SourceID

DraftID = str


@dataclass
class Draft:
    draftId: DraftID
    sourceId: SourceID


@dataclass
class DraftUpdate:
    sourceId: SourceID


class DraftRepository(ABC):
    @abstractmethod
    def get_draft(self, draftId: DraftID) -> Draft:
        raise NotImplementedError

    @abstractmethod
    def add_draft(self, draft: Draft) -> Draft:
        raise NotImplementedError

    @abstractmethod
    def update_draft(self, draftId: DraftID, update: DraftUpdate) -> Draft:
        raise NotImplementedError


class MemoryDraftRepository(DraftRepository):
    def get_draft(self, draftId: DraftID) -> Draft:
        source = SourceID(0)
        draftId = DraftID(0)
        return Draft(draftId, source)

    def add_draft(self, draft: Draft) -> Draft:
        return draft

    def update_draft(self, draftId: DraftID, update: DraftUpdate) -> Draft:
        return self.get_draft(draftId)
