from dataclasses import dataclass
from sigili.repository import Repository

from sigili.subscription import SubURL, SubURLCollection, Subscription
from sigili.title import TitleCollection
from sigili.type.id import Label


@dataclass
class InboxRow():
    rowId: int
    url: SubURL
    label: Label
    size: int


class Inbox():
    def __init__(self, subs: SubURLCollection,  titles: TitleCollection) -> None:
        self.subs = subs
        self.titles = titles
        pass

    def get_inbox(self):
        # TODO Optimize. No one likes this many loops.
        count = 0
        for sub in self.subs.get_sub_urls():
            repo = Repository(sub.url)
            remote = repo.titles
            subscription = Subscription(self.titles, remote)
            for update in subscription.get_updates():
                size = len(update.content)
                if (update.editOf is not None):
                    size -= len(update.editOf.content)
                yield InboxRow(count, sub, update.label, size)
