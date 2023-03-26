from hypothesis import given, strategies as st
from sigili.article.repository import ArticleDetails

from sigili.draft.source import MemorySourceRepository, Source
from sigili.type.id import SHA224, ArticleID, ContentID, SourceID


@st.composite
def an_id(draw: st.DrawFn):
    _id = draw(st.from_regex(SHA224, fullmatch=True))
    return _id


@st.composite
def a_source_id(draw: st.DrawFn):
    sourceId = draw(an_id())
    return SourceID(sourceId)


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
    source = Source(sourceId, article.articleId)
    assert repo.add_source(sourceId, article) == source


@given(a_source_id(), an_article())
def test_should_get_source(sourceId: SourceID, article: ArticleDetails):
    repo = MemorySourceRepository()
    source = Source(sourceId, article.articleId)
    repo.add_source(sourceId, article)
    assert repo.get_source(sourceId) == source
