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


@st.composite
def an_article_update(draw: st.DrawFn):
    content = draw(st.binary())
    groups = draw(st.lists(st.text()))
    editOf = draw(st.one_of(an_id(), st.none()))
    article = ArticleUpdate(
        content,
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


@given(a_source_id(), an_article(), an_article())
def test_should_do_update_source(sourceId: SourceID, base_article: ArticleDetails, update_article: ArticleDetails):
    repo = MemorySourceRepository()
    repo.add_source(sourceId, base_article)
    source = Source(sourceId, update_article.articleId)
    assert repo.update_source(sourceId, update_article) == source


@given(a_draft_id(), a_source_id(), an_article_update(), an_article_update())
def test_should_do_should_update(draftId: DraftID, sourceId: SourceID, first_update: ArticleUpdate, second_update: ArticleUpdate):
    source_repo = MemorySourceRepository()
    article_repo = MemoryArticleRepository()
    article = article_repo.add_article(first_update)
    source_repo.add_source(sourceId, article)
    draft = Draft(draftId, sourceId)
    article = article_repo.add_article(second_update)
    source_repo.add_source(sourceId, article)

    should_update = source_repo.should_update(draft)
    assert should_update == True
