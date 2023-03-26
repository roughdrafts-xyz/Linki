from sigili.draft.repository import Draft, MemoryDraftRepository
from hypothesis import given, strategies as st
from sigili.type.id import SHA224, ContentID, SourceID


st_id = st.from_regex(SHA224, fullmatch=True)


@st.composite
def an_id(draw: st.DrawFn):
    _id = draw(st.from_regex(SHA224, fullmatch=True))
    return _id


@st.composite
def a_source_id(draw: st.DrawFn):
    sourceId = draw(an_id())
    return SourceID(sourceId)


@st.composite
def a_content_id(draw: st.DrawFn):
    sourceId = draw(an_id())
    return ContentID(sourceId)


@st.composite
def some_groups(draw: st.DrawFn):
    groups = draw(st.lists(st.text()))
    return groups


@st.composite
def a_draft(draw: st.DrawFn):
    sourceId = draw(a_source_id())
    groups = draw(some_groups())
    contentId = draw(a_content_id())
    return Draft(sourceId, contentId, groups)


@given(a_draft())
def test_should_add_draft(draft):
    repo = MemoryDraftRepository()
    assert repo.set_draft(draft) == draft


@given(a_draft())
def test_should_get_draft(draft):
    repo = MemoryDraftRepository()
    draft = repo.set_draft(draft)
    assert repo.get_draft(draft.sourceId) == draft
