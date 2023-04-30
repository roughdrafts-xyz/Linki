from dataclasses import dataclass
from difflib import unified_diff
from itertools import groupby
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
        refusals = self.repo.config.get_refusals()
        for sub in self.repo.subs.get_urls():
            repo = Repository(sub.url)
            remote = repo.titles
            subscription = Subscription(self.repo.titles, remote)
            for update in subscription.get_updates():
                change = Change(
                    article=update,
                    source=sub.url
                )
                if (change.change_id in refusals):
                    continue
                self.repo.changes.add_change(change)

    def read_inbox(self):
        def sort_by_key(x): return x.source
        changes = sorted(self.repo.changes.get_changes(), key=sort_by_key)
        changes = groupby(changes, sort_by_key)
        for url, updates in changes:
            updates = list(updates)
            for update in updates:
                update.changes = self.repo.titles.get_title(update.label)
            yield InboxRow(
                url=url,
                updates=iter(updates)
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
        removes = ''
        if (copy.changes is not None):
            removes = copy.changes.content.splitlines()

        adds = copy.article.content.splitlines()
        diff = unified_diff(removes, adds, fromfile='Removes', tofile='Adds')
        styled_diff = ''
        for line in [next(diff) for _ in range(3)]:
            styled_diff += f'╎{line}'
        for line in diff:
            styled_diff += f'╎{line}\n'
        output = (''
                  + header
                  + line_top
                  + styled_diff
                  + line_bottom
                  + f'└{copy.source}'
                  )
        return output

    def approve(self, copy_id):
        change = self.read_copy(copy_id)
        if (change is None):
            return False
        self.repo.titles.set_title(change.article)
        self.repo.config.add_approval(change.change_id)
        self.repo.changes.remove_change(change)

    def refuse(self, copy_id):
        change = self.read_copy(copy_id)
        if (change is None):
            return False
        self.repo.config.add_refusal(change.change_id)
        self.repo.changes.remove_change(change)
