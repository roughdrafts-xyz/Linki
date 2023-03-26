from hypothesis import given, strategies as st
from sigili.article.repository import ArticleDetails

from sigili.draft.source import MemorySourceRepository, Source
from sigili.type.id import SHA224


st_id = st.from_regex(SHA224, fullmatch=True)


@given(st_id, st_id, st_id, st_id, st.one_of(st_id, st.none()))
def test_should_add_source(sourceId, articleId, contentId, groups, editOf):
    repo = MemorySourceRepository()
    article = ArticleDetails(articleId, contentId, groups, editOf)
    source = Source(sourceId, articleId)
    assert repo.add_source(sourceId, article) == source
