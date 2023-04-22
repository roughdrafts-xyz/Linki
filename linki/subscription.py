from dataclasses import dataclass
from typing import Iterator
from linki.draft import BaseArticle, Draft
from linki.title import TitleCollection


@dataclass
class Subscription():
    titles: TitleCollection
    remote: TitleCollection

    def get_updates(self) -> Iterator[BaseArticle]:
        for title in self.remote.get_titles():
            current = self.titles.get_title(title.label)
            editOf = current
            draft = Draft(
                title.label,
                title.content,
                editOf
            )
            if (draft.should_update()):
                yield draft
