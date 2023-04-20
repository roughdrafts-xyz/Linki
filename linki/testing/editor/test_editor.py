
from typing import Dict, List
from unittest import TestCase

from hypothesis import assume, given
from linki.article import Article
from linki.connection import Connection, MemoryConnection
from linki.draft import Draft

from linki.editor import Editor
from linki.repository import Repository, RepositoryConnection
from linki.testing.strategies.article import an_article
from linki.testing.strategies.draft import a_draft, a_new_draft, some_drafts, some_new_drafts

test = TestCase()


class MemoryRepoConnection(RepositoryConnection):
    def __init__(self) -> None:
        self.connections: Dict[str, MemoryConnection] = dict()

    def get_style(self, style: str) -> Connection:
        conn = self.connections.get(style)
        if conn is None:
            conn = MemoryConnection()
            self.connections[style] = conn
        return conn


class MemoryRepository(Repository):
    def __init__(self) -> None:
        self.connection = MemoryRepoConnection()

    def clear(self):
        self.__init__()


@given(a_new_draft())
def test_get_updates(draft: Draft):
    repo = MemoryRepository()
    editor = Editor(repo)

    repo.drafts.set_draft(draft)
    draft_count = list(editor.get_updates())
    assert len(draft_count) == 1
    test.assertCountEqual([draft], draft_count)


@given(a_new_draft())
def test_does_publish_new_draft(draft: Draft):
    repo = MemoryRepository()
    editor = Editor(repo)

    repo.drafts.set_draft(draft)
    assert editor.publish_drafts() == 1
    test.assertCountEqual(
        [title.label for title in repo.titles.get_titles()],
        [draft.label]
    )


@given(a_draft())
def test_does_publish_draft(draft: Draft):
    repo = MemoryRepository()
    editor = Editor(repo)

    repo.drafts.set_draft(draft)
    assert editor.publish_drafts() == 1
    assert draft.label in [title.label for title in repo.titles.get_titles()]
    # editOf can create two titles instead of just one. (New Title and Redirect)


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    repo = MemoryRepository()
    editor = Editor(repo)

    for draft in some_drafts:
        repo.drafts.set_draft(draft)

    updates = editor.publish_drafts()
    assert 0 < updates <= 2
    titles = [title.label for title in repo.titles.get_titles()]
    for draft in some_drafts:
        assert draft.label in titles


@given(some_drafts(2))
def test_does_publish_some_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    repo = MemoryRepository()
    editor = Editor(repo)

    for draft in some_drafts:
        repo.drafts.set_draft(draft)
    updates = editor.publish_drafts()
    assert 0 < updates <= 2
    titles = [title.label for title in repo.titles.get_titles()]
    for draft in some_drafts:
        assert draft.label in titles


@given(an_article())
def test_does_copy(update: Article):
    r_repo = MemoryRepository()
    l_repo = MemoryRepository()
    l_editor = Editor(l_repo)

    article = r_repo.articles.merge_article(update)
    r_repo.titles.set_title(article)

    assert l_editor.copy_articles(r_repo.articles) == 1
    assert l_editor.copy_titles(r_repo.titles) == 1

    test.assertCountEqual(r_repo.articles.get_articles(),
                          l_repo.articles.get_articles())
    test.assertCountEqual(r_repo.titles.get_titles(),
                          l_repo.titles.get_titles())


@given(a_draft())
def test_does_publish_changed_draft_path(draft: Draft):
    repo = MemoryRepository()
    editor = Editor(repo)

    draft.label.path = ['initial'] + draft.label.path
    init = draft.label
    assume(draft.should_update())
    repo.drafts.set_draft(draft)
    assert editor.publish_drafts() == 1
    test.assertCountEqual(
        [title.label for title in repo.titles.get_titles()],
        [init]
    )

    draft.label.path[0] = 'changed'
    changed = draft.label
    assume(draft.should_update())
    repo.drafts.set_draft(draft)
    assert editor.publish_drafts() == 1
    test.assertCountEqual(
        [title.label for title in repo.titles.get_titles()],
        [init, changed]
    )
