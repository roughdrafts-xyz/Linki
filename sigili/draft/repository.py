
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator
from sigili.article.repository import Article, ArticleUpdate
from sigili.connection import Connection, MemoryConnection, PathConnection

from sigili.type.id import ContentID, Label


@dataclass
class Draft:
    title: Label
    content: bytes
    groups: list[Label]
    editOf: Article | None = None
    _contentId: ContentID | None = field(init=False, repr=False, default=None)

    @property
    def contentId(self):
        if (self._contentId is None):
            self._contentId = ContentID.getContentID(self.content)
        return self._contentId

    def should_update(self) -> bool:
        if (self.editOf is None):
            return True
        groups_different = self.groups != self.editOf.groups
        content_different = self.contentId != self.editOf.contentId
        return groups_different or content_different

    def asArticleUpdate(self):
        _groups = [_group.name for _group in self.groups]
        _title = self.title.name
        if (self.editOf is not None):
            return ArticleUpdate(
                _title,
                self.content,
                _groups,
                self.editOf.articleId
            )
        return ArticleUpdate(
            _title,
            self.content,
            _groups,
        )


class DraftRepository(ABC):
    drafts: Connection[Draft]

    def set_draft(self, draft: Draft) -> Draft:
        self.drafts[draft.title.labelId] = draft
        return draft

    def get_draft(self, title: Label) -> Draft | None:
        return self.drafts.get(title.labelId, None)

    def get_drafts(self) -> Iterator[Draft]:
        return self.drafts.values().__iter__()

    def clear_draft(self, title: Label) -> bool:
        if (title.labelId in self.drafts):
            del self.drafts[title.labelId]
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
