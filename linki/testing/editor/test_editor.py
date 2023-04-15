
from typing import List
from unittest import TestCase

from hypothesis import given
from linki.article import Article, ArticleCollection
from linki.connection import MemoryConnection
from linki.draft import Draft, DraftCollection

from linki.editor import Editor
from linki.testing.strategies.article import an_article
from linki.testing.strategies.draft import a_draft, a_new_draft, some_drafts, some_new_drafts
from linki.title import Title, TitleCollection


@given(a_new_draft())
def test_get_updates(draft: Draft):
    titles = TitleCollection(MemoryConnection[Title]())
    drafts = DraftCollection(MemoryConnection[Draft]())
    articles = ArticleCollection(MemoryConnection[Article]())
    editor = Editor(titles, drafts, articles)

    drafts.set_draft(draft)
    draft_count = list(editor.get_updates())
    assert len(draft_count) > 0

    test = TestCase()
    test.assertCountEqual([draft], draft_count)


@given(a_new_draft())
def test_does_publish_new_draft(draft: Draft):
    titles = TitleCollection(MemoryConnection[Title]())
    drafts = DraftCollection(MemoryConnection[Draft]())
    articles = ArticleCollection(MemoryConnection[Article]())
    editor = Editor(titles, drafts, articles)

    drafts.set_draft(draft)

    editor.publish_drafts()

    draft_count = [draft.label for draft in drafts.get_drafts()]
    title_count = [title.label for title in titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, draft_count)


@given(a_draft())
def test_does_publish_draft(draft: Draft):
    titles = TitleCollection(MemoryConnection[Title]())
    drafts = DraftCollection(MemoryConnection[Draft]())
    articles = ArticleCollection(MemoryConnection[Article]())
    editor = Editor(titles, drafts, articles)

    drafts.set_draft(draft)

    editor.publish_drafts()

    title_count = [title.label for title in titles.get_titles()]
    update_count = [draft.label for draft in editor.get_updates()]

    test = TestCase()
    test.assertCountEqual(title_count, update_count)


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    titles = TitleCollection(MemoryConnection[Title]())
    drafts = DraftCollection(MemoryConnection[Draft]())
    articles = ArticleCollection(MemoryConnection[Article]())
    editor = Editor(titles, drafts, articles)

    for draft in some_drafts:
        drafts.set_draft(draft)

    editor.publish_drafts()

    draft_count = [draft.label for draft in drafts.get_drafts()]
    title_count = [title.label for title in titles.get_titles()]
    update_count = [draft.label for draft in editor.get_updates()]

    test = TestCase()
    test.assertCountEqual(title_count, draft_count)
    test.assertCountEqual(title_count, update_count)
    test.assertCountEqual(draft_count, update_count)


@given(some_drafts(2))
def test_does_publish_some_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    titles = TitleCollection(MemoryConnection[Title]())
    drafts = DraftCollection(MemoryConnection[Draft]())
    articles = ArticleCollection(MemoryConnection[Article]())
    editor = Editor(titles, drafts, articles)

    for draft in some_drafts:
        drafts.set_draft(draft)

    editor.publish_drafts()

    update_count = [draft.label for draft in editor.get_updates()]
    title_count = [title.label for title in titles.get_titles()]

    test = TestCase()
    test.assertCountEqual(title_count, update_count)


@given(an_article())
def test_does_copy(update: Article):
    r_articles = ArticleCollection(MemoryConnection[Article]())
    r_titles = TitleCollection(MemoryConnection[Title]())

    titles = TitleCollection(MemoryConnection[Title]())
    drafts = DraftCollection(MemoryConnection[Draft]())
    articles = ArticleCollection(MemoryConnection[Article]())
    editor = Editor(titles, drafts, articles)

    article = r_articles.merge_article(update)
    r_titles.set_title(article)

    editor.copy_articles(r_articles)
    test = TestCase()

    test.assertCountEqual(r_articles.get_articles(),
                          articles.get_articles())

    editor.copy_titles(r_titles)

    test.assertCountEqual(r_titles.get_titles(),
                          titles.get_titles())
