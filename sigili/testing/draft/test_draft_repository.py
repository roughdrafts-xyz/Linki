from sigili.draft.repository import MemoryDraftRepository
from hypothesis import given
from sigili.testing.strategies.draft import a_draft


@given(a_draft())
def test_should_add_draft(draft):
    repo = MemoryDraftRepository()
    assert repo.set_draft(draft) == draft


@given(a_draft())
def test_should_get_draft(draft):
    repo = MemoryDraftRepository()
    draft = repo.set_draft(draft)
    assert repo.get_draft(draft.source.articleId) == draft
