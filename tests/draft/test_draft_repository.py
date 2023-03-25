
from sigili.draft import SourceID
from sigili.draft.repository import Draft, DraftID, DraftUpdate, MemoryDraftRepository
from hypothesis import given, strategies as st, example


@given(st.text(), st.text())
@example('123', '123')
def test_should_add_draft(sourceId, draftId):
    repo = MemoryDraftRepository()
    draft = Draft(draftId, sourceId)
    assert repo.add_draft(draft) == draft


@given(st.text(), st.text())
@example('123', '123')
def test_should_get_draft(sourceId, draftId):
    repo = MemoryDraftRepository()
    draft = Draft(draftId, sourceId)
    repo.add_draft(draft)
    assert repo.get_draft(draftId) == draft


@given(st.text(), st.text(), st.text())
@example('123', '123', '123')
def test_should_update_draft(draftId, sourceId,  newSourceId):
    repo = MemoryDraftRepository()
    draft = Draft(draftId, sourceId)
    repo.add_draft(draft)
    update = DraftUpdate(newSourceId)

    expected_draft = Draft(draftId, SourceID(newSourceId))

    new_draft = repo.update_draft(draftId, update)
    assert new_draft == expected_draft
    assert new_draft != draft
