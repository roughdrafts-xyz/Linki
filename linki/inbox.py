from dataclasses import dataclass
from linki.repository import Repository
from linki.subscription import Subscription

from linki.title import TitleCollection
from linki.id import SimpleLabel
from linki.url import URL, URLCollection


@dataclass
class InboxRow():
    rowId: int
    url: URL
    label: SimpleLabel
    size: int


class Inbox():
    def __init__(self, subs: URLCollection,  titles: TitleCollection) -> None:
        self.subs = subs
        self.titles = titles

    def get_inbox(self):
        # TODO Optimize. No one likes this many loops.
        count = 0
        for sub in self.subs.get_urls():
            repo = Repository(sub.url)
            remote = repo.titles
            subscription = Subscription(self.titles, remote)
            for update in subscription.get_updates():
                size = len(update.content)
                if (update.editOf is not None):
                    size -= len(update.editOf.content)
                yield InboxRow(count, sub, update.label, size)
