
from typing import List
from unittest import TestCase

from hypothesis import given

from sigili.article.repository import ArticleUpdate, MemoryArticleRepository
from sigili.editor import Editor
from sigili.draft.repository import Draft, MemoryDraftRepository
from sigili.testing.strategies.article import an_article_update
from sigili.testing.strategies.draft import a_draft, a_new_draft, some_drafts, some_new_drafts
from sigili.title.repository import MemoryTitleRepository, Title


@given(a_new_draft())
def test_get_updates(draft: Draft):
    titles = MemoryTitleRepository()
    drafts = MemoryDraftRepository()
    articles = MemoryArticleRepository()
    editor = Editor(titles, drafts, articles)

    drafts.set_draft(draft)
    draft_count = list(editor.get_updates())
    assert len(draft_count) > 0

    test = TestCase()
    test.assertCountEqual([draft], draft_count)


@given(an_article_update())
def test_loads_titles(update: ArticleUpdate):
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository()
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts, articles)

    article = articles.add_article(update)
    _title = titles.set_title(article.title, article)
    assert _title is not None

    editor.load_titles()
    _draft = drafts.get_draft(_title.title)
    assert _draft is not None

    assert _draft.title == _title.title
    assert _draft.content == articles.content.get_content(
        _title.contentId)
    test = TestCase()
    test.assertCountEqual(_draft.groups, _title.groups)
    assert _draft.editOf == _title
    assert _draft.editOf == Title.fromArticle(article)


@given(a_new_draft())
def test_does_publish_new_draft(draft: Draft):
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository()
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts, articles)

    drafts.set_draft(draft)

    editor.publish_drafts()

    draft_count = [draft.title for draft in drafts.get_drafts()]
    title_count = [title.title for title in titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, draft_count)


@given(a_draft())
def test_does_publish_draft(draft: Draft):
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository()
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts, articles)

    drafts.set_draft(draft)

    editor.publish_drafts()

    title_count = [title.title for title in titles.get_titles()]
    update_count = [draft.title for draft in editor.get_updates()]

    test = TestCase()
    test.assertCountEqual(title_count, update_count)


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository()
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts, articles)

    for draft in some_drafts:
        drafts.set_draft(draft)

    editor.publish_drafts()

    draft_count = [draft.title for draft in drafts.get_drafts()]
    title_count = [title.title for title in titles.get_titles()]
    update_count = [draft.title for draft in editor.get_updates()]

    test = TestCase()
    test.assertCountEqual(title_count, draft_count)
    test.assertCountEqual(title_count, update_count)
    test.assertCountEqual(draft_count, update_count)


@given(some_drafts(2))
def test_does_publish_some_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    articles = MemoryArticleRepository()
    titles = MemoryTitleRepository()
    drafts = MemoryDraftRepository()
    editor = Editor(titles, drafts, articles)

    for draft in some_drafts:
        drafts.set_draft(draft)

    editor.publish_drafts()

    update_count = [draft.title for draft in editor.get_updates()]
    title_count = [title.title for title in titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, update_count)
