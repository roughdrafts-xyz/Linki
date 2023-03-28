
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
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
        self._folder = path
        self._drafts = path.joinpath('drafts')

    def _write_draft_data(self, draft: Draft):
        with self._drafts.joinpath(draft.title.name, 'data').open('w') as _jsonPath:
            _draft = asdict(draft)
            del _draft['content']
            json.dump(_draft, _jsonPath)

    def _get_draft_data(self, title: Label):
        with self._drafts.joinpath(title.name).open() as _jsonPath:
            _json = json.load(_jsonPath)
            return _json

    def set_draft(self, draft: Draft) -> Draft:
        _draft = self._drafts.joinpath(draft.title.name)
        _draft.mkdir(exist_ok=True)
        _draft.joinpath('content').write_bytes(draft.content)
        self._write_draft_data(draft)
        last_path = self._drafts
        for group in draft.groups:
            last_path = self._folder.joinpath(group)
            last_path.mkdir()
        last_path.symlink_to(self._drafts.joinpath(draft.title.name))
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
            title,
            _content,
            _data.get('groups', []),
            _data.get('editOf', None)
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
        return _titlePath.resolve()
