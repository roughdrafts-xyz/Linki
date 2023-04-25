from dataclasses import dataclass
from typing import Iterator
from linki.change import Change, ChangeLabel
from linki.repository import Repository
from linki.subscription import Subscription


# start a counter
# for every id[0:counter], see if any match across ids
# if yes, increase counter and try again until there are no matches.

# store inbox IDs somewhere so that we can reverse them into url&path on Copy


@dataclass
class InboxRow():
    url: str
    updates: Iterator[Change]


class Inbox():
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def load_inbox(self):
        for sub in self.repo.subs.get_urls():
            repo = Repository(sub.url)
            remote = repo.titles
            subscription = Subscription(self.repo.titles, remote)
            for update in subscription.get_updates():
                size = len(update.content)
                if (update.editOf is not None):
                    size -= len(update.editOf.content)
                change = Change(
                    size=size,
                    article=update,
                    url=sub
                )
                self.repo.changes.add_change(change)

    def read_inbox(self):
        for sub in self.repo.subs.get_urls():
            yield InboxRow(
                url=sub.url,
                updates=self.repo.changes.get_changes(sub)
            )
