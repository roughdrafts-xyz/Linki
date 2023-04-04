
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import pickle
from typing import Iterator
from sigili.article.repository import Article, ArticleUpdate

from sigili.type.id import ArticleID, ContentID, Label, LabelID


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
        if (self.editOf is not None):
            return ArticleUpdate(
                self.title,
                self.content,
                self.groups,
                self.editOf.articleId
            )
        return ArticleUpdate(
            self.title,
            self.content,
            self.groups
        )


@dataclass
class SparseDraft:
    title: Label
    groups: list[Label]
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
    def clear_draft(self, title: Label) -> bool:
        raise NotImplementedError


class MemoryDraftRepository(DraftRepository):
    def __init__(self) -> None:
        self.drafts: dict[LabelID, Draft] = dict()

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


class FileSystemDraftRepository(DraftRepository):
    def __init__(self, path: Path) -> None:
        self._path = path.resolve()
        self._content = self._path.joinpath('content')
        self._data = self._path.joinpath('data')

    def dump_draft(self, draft: Draft, path: Path) -> SparseDraft:
        with path.open('wb') as _path:
            _draft = SparseDraft.fromDraft(draft)
            pickle.dump(_draft, _path)
            return _draft

    def load_draft(self, path: Path) -> SparseDraft:
        with path.open('rb') as _path:
            _draft = pickle.load(_path)
            return _draft

    def set_draft(self, draft: Draft) -> Draft:
        _content = self._content.joinpath(draft.title.name)
        _data = self._data.joinpath(draft.title.name)
        _content.write_bytes(draft.content)
        self.dump_draft(draft, _data)
        return draft

    def get_draft(self, title: Label) -> Draft | None:
        content_path = self._content.joinpath(title.name)
        data_path = self._data.joinpath(title.name)
        if (not (content_path.exists() and data_path.exists())):
            return None
        _content = content_path.read_bytes()
        _data = self.load_draft(data_path)
        return Draft(
            _data.title,
            _content,
            _data.groups,
            _data.editOf
        )

    def get_drafts(self) -> Iterator[Draft]:
        for draft in self._data.iterdir():
            title = Label(draft.name)
            _draft = self.get_draft(title)
            if (_draft is not None):
                yield _draft

    def clear_draft(self, title: Label) -> bool:
        content_path = self._content.joinpath(title.name)
        data_path = self._data.joinpath(title.name)
        if (not (content_path.exists() and data_path.exists())):
            return False
        content_path.unlink()
        data_path.unlink()
        return True

    @staticmethod
    def init(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _draftPath = path.joinpath('drafts')
        _draftPath.mkdir()

        _contentPath = _draftPath.joinpath('content')
        _contentPath.mkdir()

        _dataPath = _draftPath.joinpath('data')
        _dataPath.mkdir()
        return _draftPath
