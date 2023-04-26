from dataclasses import dataclass
from typing import Iterator
from linki.change import Change
from linki.connection import CountError
from linki.repository import Repository
from linki.subscription import Subscription


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
                change = Change(
                    article=update,
                    url=sub
                )
                self.repo.changes.add_change(change)

    def read_inbox(self):
        for sub in self.repo.subs.get_urls():
            # Optimize IDs here
            # start a counter
            # for every id[0:counter], see if any match across ids
            # if yes, increase counter and try again until there are no matches.

            # store inbox IDs somewhere so that we can reverse them into url&path on Copy
            changes = self.repo.changes.get_changes(sub)
            for change in changes:
                change.changes = self.repo.titles.get_title(change.label)

            yield InboxRow(
                url=sub.url,
                updates=changes
            )

    def read_copy(self, copy_id: str):
        matches = self.repo.changes.find_change_id(copy_id)
        if (len(matches) > 1):
            raise CountError(matches)
        change_id = matches[0]
        change = self.repo.changes.get_change(change_id)
        if (change is None):
            return None
        change.changes = self.repo.titles.get_title(change.label)
        return change
