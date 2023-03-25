
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sigili.draft import SourceID


@dataclass
class Draft:
    sourceId: SourceID


class DraftRepository(ABC):
    @abstractmethod
    def should_update(self, draft: Draft):
        pass
