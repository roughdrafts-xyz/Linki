from abc import ABC
from dataclasses import dataclass
from typing import Iterator
from linki.article import Article
from linki.connection import Connection

from linki.id import Label


@dataclass
class Draft(Article):
    label: Label
    content: str
    editOf: Article | None = None

    def should_update(self) -> bool:
        if (self.editOf is None):
            return True
        label_different = self.label != self.editOf.label
        content_different = self.content != self.editOf.content
        return label_different or content_different

    @classmethod
    def fromArticle(cls, article: Article) -> 'Draft':
        return cls(
            article.label,
            article.content,
            article.editOf
        )

    def __hash__(self) -> int:
        return super().__hash__()


class DraftCollection(ABC):
    def __init__(self, connection: Connection[Draft]) -> None:
        self.drafts = connection

    def set_draft(self, draft: Draft) -> Draft:
        self.drafts[draft.label.labelId] = draft
        return draft

    def get_draft(self, label: Label) -> Draft | None:
        return self.drafts.get(label.labelId, None)

    def get_drafts(self) -> Iterator[Draft]:
        for item in self.drafts.values():
            yield item

    def clear_draft(self, label: Label) -> bool:
        if (label.labelId in self.drafts):
            del self.drafts[label.labelId]
            return True
        return False
