from hypothesis import given, strategies as st
from sigili.article.repository import ArticleDetails, ArticleUpdate, MemoryArticleRepository
from sigili.draft.repository import Draft

from sigili.draft.source import MemorySourceRepository, Source
from sigili.type.id import SHA224, ArticleID, ContentID, DraftID, SourceID


@st.composite
def an_id(draw: st.DrawFn):
    _id = draw(st.from_regex(SHA224, fullmatch=True))
    return _id


@st.composite
def a_source_id(draw: st.DrawFn):
    sourceId = draw(an_id())
    return SourceID(sourceId)


@st.composite
def a_draft_id(draw: st.DrawFn):
    draftId = draw(an_id())
    return DraftID(draftId)


@st.composite
def an_article(draw: st.DrawFn):
    articleId = draw(an_id())
    contentId = draw(an_id())
    groups = draw(st.lists(st.text()))
    editOf = draw(st.one_of(an_id(), st.none()))
    article = ArticleDetails(
        ArticleID(articleId),
        ContentID(contentId),
        groups,
    )
    if (editOf is not None):
        article.editOf = ArticleID(editOf)
    return article


@given(a_source_id(), an_article())
def test_should_add_source(sourceId: SourceID, article: ArticleDetails):
    repo = MemorySourceRepository()
    source = Source(sourceId, article.articleId,
                    article.contentId, article.groups)
    assert repo.set_source(sourceId, article) == source


@given(a_source_id(), an_article())
def test_should_get_source(sourceId: SourceID, article: ArticleDetails):
    repo = MemorySourceRepository()
    source = Source(sourceId, article.articleId,
                    article.contentId, article.groups)
    repo.set_source(sourceId, article)
    assert repo.get_source(sourceId) == source


@given(a_source_id(), an_article(), an_article())
def test_should_flag_update(sourceId: SourceID, source_article: ArticleDetails, draft_article: ArticleDetails):
    source_repo = MemorySourceRepository()
    source = source_repo.set_source(sourceId, source_article)
    draft = Draft(sourceId, draft_article.contentId, draft_article.groups)

    should_update = source_repo.should_update(draft)
    expected = ((draft.groups != source.groups) or (
        draft.contentId != source.contentId))

    assert should_update == expected


@given(a_source_id(), an_article())
def test_should_flag_update_for_new_file(sourceId: SourceID, draft_article: ArticleDetails):
    source_repo = MemorySourceRepository()
    draft = Draft(sourceId, draft_article.contentId, draft_article.groups)

    should_update = source_repo.should_update(draft)
    expected = True

    assert should_update == expected


@given(a_source_id(), an_article())
def test_should_not_flag_non_update(sourceId: SourceID, article: ArticleDetails):
    source_repo = MemorySourceRepository()
    source_repo.set_source(sourceId, article)
    draft = Draft(sourceId, article.contentId, article.groups)

    should_update = source_repo.should_update(draft)
    expected = False

    assert should_update == expected
