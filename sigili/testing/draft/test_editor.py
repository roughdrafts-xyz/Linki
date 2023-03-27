
from unittest import TestCase

from hypothesis import given
from sigili.article.repository import MemoryArticleRepository
from sigili.draft.editor import Editor
from sigili.draft.repository import Draft, MemoryDraftRepository
from sigili.testing.strategies.draft import a_draft
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

    titles.set_title(draft.title, draft.asArticleUpdate())
    editor.load_titles()

    draft_count = list(drafts.get_drafts())
    print(draft_count)
    test = TestCase()
    test.assertCountEqual([draft], draft_count)


# @given(a_draft(), a_draft())
# def test_does_publish_drafts(base_draft: Draft, new_draft: Draft):
#    repo = ControlArticleRepository()
#    titles = MemoryTitleRepository(repo)
#    drafts = MemoryDraftRepository()
#    editor = Editor(repo, titles, drafts)

#    titles.set_title(base_draft.editOf.title, base_draft.editOf)

#    new_draft.editOf = base_draft.editOf
#    drafts.set_draft(new_draft)

#    editor.publish_drafts()

#    draft_count = [draft.editOf.articleId for draft in drafts.get_drafts()]
#    title_count = [title.articleId for title in titles.get_titles()]

#    test = TestCase()

#    test.assertCountEqual(title_count, draft_count)
