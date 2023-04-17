from dataclasses import dataclass
from linki.contribution import Contribution
from linki.repository import Repository
from linki.subscription import Subscription

from linki.title import TitleCollection
from linki.id import Label
from linki.url import URL, URLCollection


class Outbox():
    def __init__(self, contribs: URLCollection) -> None:
        self.contribs = contribs

    def send_updates(self) -> int:
        count = 0
        for contrib in self.contribs.get_urls():
            contribution = Contribution(contrib)
            contribution.announce_updates()
        return count
