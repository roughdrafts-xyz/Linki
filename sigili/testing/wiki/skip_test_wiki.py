from hypothesis import given
from sigili.article.repository import ArticleRepository
from sigili.wiki import Wiki


@given(a_wiki_with_an_update())
def test_should_publish_update(wiki: Wiki):
    articles: ArticleRepository = wiki.articles
    assert wiki.get_updates() == articles.get_articleIds()


@given(a_wiki_with_an_update(), a_wiki())
def test_should_download_update(updated_wiki: Wiki, new_wiki: Wiki):
    assert sorted(new_wiki.articles.articleIds()) != sorted(
        updated_wiki.articles.articleIds())
    updates = updated_wiki.get_updates()
    new_wiki.merge_updates(updates)
    assert sorted(new_wiki.articles.articleIds()) == sorted(
        updated_wiki.articles.articleIds())
    pass
