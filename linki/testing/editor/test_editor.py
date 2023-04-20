
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
    print(draft)
    print(draft_count)
    assert len(draft_count) > 0

    test = TestCase()
    test.assertCountEqual([draft], draft_count)


@given(a_new_draft())
def test_does_publish_new_draft(draft: Draft):
    repo = MemoryRepository()
    editor = Editor(repo)

    repo.drafts.set_draft(draft)

    draft_count = [draft.label for draft in repo.drafts.get_drafts()]

    editor.publish_drafts()

    title_count = [title.label for title in repo.titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, draft_count)


@given(a_draft())
def test_does_publish_draft(draft: Draft):
    repo = MemoryRepository()
    editor = Editor(repo)

    repo.drafts.set_draft(draft)

    update_count = [draft.label for draft in editor.get_updates()]

    editor.publish_drafts()

    title_count = [title.label for title in repo.titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, update_count)


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    repo = MemoryRepository()
    editor = Editor(repo)

    for draft in some_drafts:
        repo.drafts.set_draft(draft)

    draft_count = [draft.label for draft in repo.drafts.get_drafts()]
    update_count = [draft.label for draft in editor.get_updates()]

    editor.publish_drafts()

    title_count = [title.label for title in repo.titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, draft_count)
    test.assertCountEqual(title_count, update_count)
    test.assertCountEqual(draft_count, update_count)


@given(some_drafts(2))
def test_does_publish_some_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    repo = MemoryRepository()
    editor = Editor(repo)

    for draft in some_drafts:
        repo.drafts.set_draft(draft)

    update_count = [draft.label for draft in editor.get_updates()]

    editor.publish_drafts()

    title_count = [title.label for title in repo.titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, update_count)


@given(an_article())
def test_does_copy(update: Article):
    r_repo = MemoryRepository()
    r_articles = r_repo.articles
    r_titles = r_repo.titles

    repo = MemoryRepository()
    editor = Editor(repo)

    article = r_articles.merge_article(update)
    r_titles.set_title(article)

    editor.copy_articles(r_articles)
    test = TestCase()

    test.assertCountEqual(r_articles.get_articles(),
                          repo.articles.get_articles())

    editor.copy_titles(r_titles)

    test.assertCountEqual(r_titles.get_titles(),
                          repo.titles.get_titles())


@given(a_draft())
def test_does_publish_changed_draft_path(draft: Draft):
    repo = MemoryRepository()
    editor = Editor(repo)

    draft.label.path = ['initial'] + draft.label.path
    assume(draft.should_update())
    repo.drafts.set_draft(draft)
    assert editor.publish_drafts() == 1

    draft.label.path[0] = 'changed'
    assume(draft.should_update())
    repo.drafts.set_draft(draft)
    assert editor.publish_drafts() == 1
