
from typing import Iterator
from unittest import TestCase

from hypothesis import given, strategies
from sigili.article.repository import Article, MemoryArticleRepository
from sigili.draft.editor import Editor
from sigili.draft.repository import Draft, MemoryDraftRepository
from sigili.testing.strategies.draft import a_draft, some_drafts
from sigili.title.repository import MemoryTitleRepository


@given(a_draft())
def test_get_updates(draft: Draft):
    repo = MemoryArticleRepository()
    titles = MemoryTitleRepository(repo)
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts)

    drafts.set_draft(draft)
    draft_count = list(editor.get_updates())

    test = TestCase()
    if (draft.should_update()):
        test.assertCountEqual([draft], draft_count)
    else:
        test.assertCountEqual([], draft_count)


@given(a_draft())
def test_loads_titles(draft: Draft):
    repo = MemoryArticleRepository()
    titles = MemoryTitleRepository(repo)
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts)

    _title = titles.set_title(draft.title, draft.asArticleUpdate())
    editor.load_titles()
    _draft = drafts.get_draft(_title.title)

    assert _draft is not None
    assert _title.title == _draft.title
    assert _draft.content == titles.articles.content.get_content(
        _title.contentId)
    assert sorted(_draft.groups) == sorted(_title.groups)
    assert _draft.editOf == _title


@given(a_draft())
def test_does_publish_new_draft(draft: Draft):
    repo = MemoryArticleRepository()
    titles = MemoryTitleRepository(repo)
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts)

    drafts.set_draft(draft)

    editor.publish_drafts()

    draft_count = [draft for draft in drafts.get_drafts()]
    title_count = [title for title in titles.get_titles()]

    if (draft.should_update()):
        assert len(draft_count) == len(title_count)
        test = TestCase()
        articles = [Article.fromArticleUpdate(
            draft.asArticleUpdate()) for draft in draft_count]
        test.assertCountEqual(title_count, articles)
    else:
        assert len(draft_count) != len(title_count)


@given(some_drafts(3))
def test_does_publish_some_drafts(some_drafts: Iterator[Draft]):
    repo = MemoryArticleRepository()
    titles = MemoryTitleRepository(repo)
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts)

    for draft in some_drafts:
        drafts.set_draft(draft)

    editor.publish_drafts()

    draft_count = [draft for draft in drafts.get_drafts()]
    title_count = [title for title in titles.get_titles()]

    for draft in draft_count:
        article = Article.fromArticleUpdate(draft.asArticleUpdate())
        if (draft.should_update()):
            assert article in title_count
        else:
            assert article not in title_count
