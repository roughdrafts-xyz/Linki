from sigili.draft.repository import Draft, DraftUpdate, MemoryDraftRepository
from hypothesis import given, strategies as st

from sigili.type.id import SHA224

st_id = st.from_regex(SHA224)


@given(st_id, st_id)
def test_should_add_draft(sourceId, draftId):
    repo = MemoryDraftRepository()
    draft = Draft(draftId, sourceId)
    assert repo.add_draft(draft) == draft


@given(st_id, st_id)
def test_should_get_draft(sourceId, draftId):
    repo = MemoryDraftRepository()
    draft = Draft(draftId, sourceId)
    repo.add_draft(draft)
    assert repo.get_draft(draftId) == draft


@given(st_id, st_id, st_id)
def test_should_update_draft(draftId, sourceId,  newSourceId):
    repo = MemoryDraftRepository()
    draft = Draft(draftId, sourceId)
    repo.add_draft(draft)
    update = DraftUpdate(newSourceId)

    expected_draft = Draft(draftId, newSourceId)

    new_draft = repo.update_draft(draftId, update)
    assert new_draft == expected_draft
    # Its okay if new drafts equal old drafts
    # assert new_draft != draft
