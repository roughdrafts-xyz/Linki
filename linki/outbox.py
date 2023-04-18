from linki.contribution import Contribution
from linki.repository import Repository


class Outbox():
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def send_updates(self) -> int:
        count = 0
        for contrib in self.repo.contribs.get_urls():
            contribution = Contribution(self.repo, contrib)
            success = contribution.announce_updates()
            if (success):
                count += 1
        return count
