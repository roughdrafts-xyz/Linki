from abc import ABC
from typing import Iterator
from linki.article import BaseArticle
from linki.connection import Connection

from linki.id import BaseLabel


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


class DraftCollection(ABC):
    def __init__(self, connection: Connection[BaseArticle]) -> None:
        self.drafts = connection

    def set_draft(self, draft: BaseArticle) -> BaseArticle:
        self.drafts[draft.label.labelId] = draft
        return draft

    def get_draft(self, label: BaseLabel) -> BaseArticle | None:
        return self.drafts.get(label.labelId, None)

    def get_drafts(self) -> Iterator[BaseArticle]:
        for item in self.drafts.values():
            yield item

    def clear_draft(self, label: BaseLabel) -> bool:
        if (label.labelId in self.drafts):
            del self.drafts[label.labelId]
            return True
        return False
