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
            changes = list(self.repo.changes.get_changes(sub))
            for change in changes:
                change.changes = self.repo.titles.get_title(change.label)

            yield InboxRow(
                url=sub.url,
                updates=iter(changes)
            )

    def render_inbox(self):
        for folder in self.read_inbox():
            output = ''
            output += f'{folder.url}\n'
            detail = next(folder.updates, None)
            while detail is not None:
                next_detail = next(folder.updates, None)
                entry = f'┤{detail.change_id}├ {detail.path} ({detail.size:+n})'
                if (next_detail) is not None:
                    output += f'├{entry}\n'
                else:
                    output += f'└{entry}'
                detail = next_detail
            yield output

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

    def render_copy(self, copy_id: str):
        copy = self.read_copy(copy_id)
        if (copy is None):
            return ''
        header_left = f'│{copy.change_id}│'
        header_right = f'{copy.path} ({copy.size:+n})'
        header = f'{header_left} {header_right}\n'

        line_left = '─' * (len(header_left)-2)
        line_right = '─' * len(header_right)
        line_top = f'├{line_left}┴{line_right}\n'
        line_bottom = f'├{line_left}─{line_right}\n'
        output = (''
                  + header
                  + line_top
                  + '╎--- Removes\n'
                  + '╎+++ Adds\n'
                  + '╎@@ -0,0 +1 @@\n'
                  + '╎+Hello World!\n'
                  + line_bottom
                  + f'└{copy.url.url}'
                  )
        return output
