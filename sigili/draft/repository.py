
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import pickle
from typing import Iterator
from sigili.article.repository import Article, ArticleUpdate

from sigili.type.id import ArticleID, ContentID, Label


@dataclass
class Draft:
    title: Label
    content: bytes
    groups: list[str]
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


@dataclass
class SparseDraft:
    title: Label
    groups: list[str]
    editOf: Article | None = None

    @classmethod
    def fromDraft(cls, draft: Draft):
        return cls(
            draft.title,
            draft.groups,
            draft.editOf
        )


class DraftRepository(ABC):
    @abstractmethod
    def set_draft(self, draft: Draft) -> Draft:
        raise NotImplementedError

    @abstractmethod
    def get_draft(self, title: Label) -> Draft | None:
        raise NotImplementedError

    @abstractmethod
    def get_drafts(self) -> Iterator[Draft]:
        raise NotImplementedError

    @abstractmethod
    def clear_draft(self, title: Label) -> None:
        raise NotImplementedError


class MemoryDraftRepository(DraftRepository):
    def __init__(self) -> None:
        self.drafts: dict[Label, Draft] = dict()

    def set_draft(self, draft: Draft) -> Draft:
        self.drafts[draft.title] = draft
        return draft

    def get_draft(self, title: Label) -> Draft | None:
        return self.drafts.get(title, None)

    def get_drafts(self) -> Iterator[Draft]:
        return self.drafts.values().__iter__()

    def clear_draft(self, title: Label) -> None:
        if (title in self.drafts):
            del self.drafts[title]


class FileSystemDraftRepository(DraftRepository):
    def __init__(self, path: Path) -> None:
        self._folder = path.resolve()
        self._drafts = path.joinpath('drafts').resolve()

    def _write_draft_data(self, draft: Draft) -> SparseDraft:
        with self._drafts.joinpath(draft.title.name, 'data').open('wb') as _path:
            _draft = SparseDraft.fromDraft(draft)
            pickle.dump(_draft, _path)
            return _draft

    def _get_draft_data(self, title: Label) -> SparseDraft:
        with self._drafts.joinpath(title.name, 'data').open('rb') as _path:
            _draft = pickle.load(_path)
            return _draft

    def set_draft(self, draft: Draft) -> Draft:
        _draft = self._drafts.joinpath(draft.title.name)
        _draft.mkdir(exist_ok=True)

        _content = _draft.joinpath('content')
        _content.write_bytes(draft.content)

        self._write_draft_data(draft)
        _draft = self.get_draft(draft.title)
        if (_draft is not None):
            return _draft
        else:
            raise LookupError

    def get_draft(self, title: Label) -> Draft | None:
        _draft = self._drafts.joinpath(title.name)
        if (not _draft.exists()):
            return None
        _content = _draft.joinpath('content').read_bytes()
        _data = self._get_draft_data(title)
        return Draft(
            _data.title,
            _content,
            _data.groups,
            _data.editOf
        )

    def get_drafts(self) -> Iterator[Draft]:
        for draft in self._drafts.iterdir():
            title = Label(draft.name)
            _draft = self.get_draft(title)
            if (_draft is not None):
                yield _draft

    def clear_draft(self, title: Label) -> None:
        _draft = self._drafts.joinpath(title.name)
        if (not _draft.exists()):
            return None
        _draft.joinpath('data').unlink()
        _draft.joinpath('content').unlink()
        _draft.rmdir()

    @staticmethod
    def initialize_directory(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _titlePath = path.joinpath('drafts')
        _titlePath.mkdir()
        return path
