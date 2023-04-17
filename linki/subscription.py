from dataclasses import dataclass
from typing import Iterator
from linki.draft import Draft
from linki.title import TitleCollection


@dataclass
class Subscription():
    titles: TitleCollection
    remote: TitleCollection

    def get_updates(self) -> Iterator[Draft]:
        for title in self.remote.get_titles():
            current = self.titles.get_title(title.label)
            editOf = None
            if (current is not None):
                editOf = current.article
            draft = Draft(
                title.label,
                title.article.content,
                editOf
            )
            if (draft.should_update()):
                yield draft
