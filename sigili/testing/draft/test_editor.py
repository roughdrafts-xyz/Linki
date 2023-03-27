
from unittest import TestCase

from hypothesis import given
from sigili.article.repository import MemoryArticleRepository
from sigili.draft.editor import Editor
from sigili.draft.repository import Draft, MemoryDraftRepository
from sigili.testing.draft.strategies import a_draft
from sigili.title.repository import MemoryTitleRepository


@given(a_draft())
def test_get_updates(draft: Draft):
    repo = MemoryArticleRepository()
    titles = MemoryTitleRepository(repo)
    drafts = MemoryDraftRepository()
    editor = Editor(repo, titles, drafts)

    drafts.set_draft(draft)
    draft_count = list(editor.get_updates())

    test = TestCase()
    if (draft.should_update()):
        test.assertCountEqual([draft], draft_count)
    else:
        test.assertCountEqual([], draft_count)

#   @given(an_article(), an_article(), strategies.binary())
#   def test_does_publish_drafts(base_article: ArticleDetails, new_article: ArticleDetails, some_content: bytes):
#       repo = MemoryArticleRepository()
#       titles = MemoryTitleRepository(repo)
#       drafts = MemoryDraftRepository()
#       editor = Editor(repo, titles, drafts)

#       title = titles.set_title(base_article.title, base_article)

#       if (title is not None):
#           drafts.set_draft(
#               Draft(base_article, some_content, new_article.contentId, new_article.groups))

#       if (title is None):
#           drafts.clear_draft(base_article.articleId)

#       editor.publish_drafts()

#       draft_count = (draft.source.articleId for draft in drafts.get_drafts())
#       title_count = (title.articleId for title in titles.get_titles())
#       article_count = (article for article in repo.get_articleIds()
#                       if article in draft_count and article in title_count)

#       test = TestCase()

#       test.assertCountEqual(title_count, draft_count)
