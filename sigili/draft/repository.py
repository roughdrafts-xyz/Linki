from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from sigili.article.repository import Article
from sigili.connection import Connection, MemoryConnection, PathConnection

from sigili.type.id import Label


@dataclass
class Draft:
    label: Label
    content: bytes
    editOf: Article | None = None

    def should_update(self) -> bool:
        if (self.editOf is None):
            return True
        label_different = self.label != self.editOf.label
        content_different = self.content != self.editOf.content
        return label_different or content_different


class DraftRepository(ABC):
    drafts: Connection[Draft]

    def set_draft(self, draft: Draft) -> Draft:
        self.drafts[draft.label.labelId] = draft
        return draft

    def get_draft(self, label: Label) -> Draft | None:
        return self.drafts.get(label.labelId, None)

    def get_drafts(self) -> Iterator[Draft]:
        return self.drafts.values().__iter__()

    def clear_draft(self, label: Label) -> bool:
        if (label.labelId in self.drafts):
            del self.drafts[label.labelId]
            return True
        return False


class MemoryDraftRepository(DraftRepository):
    def __init__(self) -> None:
        self.drafts = MemoryConnection()


class FileSystemDraftRepository(DraftRepository):
    def __init__(self, path: Path) -> None:
        self.drafts = PathConnection(path.resolve())

    @staticmethod
    def init(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _draftPath = path.joinpath('drafts')
        _draftPath.mkdir()
        return _draftPath
