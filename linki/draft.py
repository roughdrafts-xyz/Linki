from pathlib import Path
from typing import Iterator

import msgspec
from linki.article import BaseArticle
from linki.connection import Connection

from linki.id import BaseLabel, InoLabel


def Draft(
    label: BaseLabel,
    content: str,
    editOf: 'BaseArticle | None'
) -> BaseArticle:
    return BaseArticle(
        label=label,
        content=content,
        editOf=editOf
    )


class DraftCollection():
    def __init__(self, connection: Connection[BaseArticle]) -> None:
        self.store = connection

    def set_draft(self, draft: BaseArticle) -> BaseArticle:
        self.store[draft.label.labelId] = draft
        return draft

    def get_draft(self, label: BaseLabel) -> BaseArticle | None:
        return self.store.get(label.labelId, None)

    def get_drafts(self) -> Iterator[BaseArticle]:
        for item in self.store.values():
            yield item

    def clear_draft(self, label: BaseLabel) -> bool:
        if (label.labelId in self.store):
            del self.store[label.labelId]
            return True
        return False


class Shadow(msgspec.Struct, frozen=True, kw_only=True):
    path: Path
    article: BaseArticle


class ShadowCollection():
    def __init__(self, connection: Connection[Shadow]) -> None:
        self.store = connection

    def add_shadow(self, article: BaseArticle, path: Path):
        label = InoLabel(path)
        self.store[label.labelId] = Shadow(
            path=path,
            article=article
        )

    def get_shadow(self, path: Path):
        label = InoLabel(path)
        return self.store.get(label.labelId, None)
