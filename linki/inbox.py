from dataclasses import dataclass
from linki.repository import Repository
from linki.subscription import Subscription

from linki.title import TitleCollection
from linki.id import BaseLabel
from linki.url import URLCollection


@dataclass
class UpdateDetails():
    size: int
    label: BaseLabel
    inbox_id: int


@dataclass
class InboxRow():
    url: str
    updates: list[UpdateDetails]


class Inbox():
    def __init__(self, subs: URLCollection,  titles: TitleCollection) -> None:
        self.subs = subs
        self.titles = titles

    def get_inbox(self):
        # TODO Optimize. No one likes this many loops.
        for sub in self.subs.get_urls():
            repo = Repository(sub.url)
            remote = repo.titles
            subscription = Subscription(self.titles, remote)
            row = InboxRow(
                url=sub.url,
                updates=[]
            )
            for update in subscription.get_updates():
                size = len(update.content)
                if (update.editOf is not None):
                    size -= len(update.editOf.content)
                details = UpdateDetails(
                    size=size,
                    label=update.label,
                    inbox_id=0
                )
                row.updates.append(details)
            yield row
