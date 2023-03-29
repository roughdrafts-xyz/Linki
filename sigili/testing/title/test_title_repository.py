from hypothesis import assume, given, strategies
import pytest
from sigili.article.repository import Article
from sigili.testing.contexts.title import getTitleRepository, styles
from sigili.testing.strategies.article import an_article, an_edit_of
from sigili.title.repository import Title

# from sigili.title.repository import TitleDetails


# CAR needs to be able to track what the CAs are.
# CAR needs to provide CAs or information about them.

# Titles is the choice of phrase for current titles


@pytest.mark.parametrize('style', styles)
@given(strategies.data())
def test_should_crud_current_title(style, data):
    with getTitleRepository(style) as repo:
        # titles only have one title, but one title can have multiple titles
        # should handle ignoring a no-op
        article: Article = data.draw(an_article())
        current_title: Title | None = repo.set_title(article.title, article)
        assert current_title != None
        assert current_title == Title.fromArticle(article)

        # should handle a new set
        article: Article = data.draw(an_article())
        current_title: Title | None = repo.set_title(article.title, article)
        assert current_title != None
        assert current_title == Title.fromArticle(article)

        # should handle a an existing title
        article: Article = data.draw(an_edit_of(article))
        current_title: Title | None = repo.set_title(article.title, article)
        assert current_title != None
        assert current_title == Title.fromArticle(article)

        # should unset a title
        current_title: Title | None = repo.clear_title(current_title.title)
        assert current_title == None


@pytest.mark.parametrize('style', styles)
@given(an_article(), an_article())
def test_should_get_title(style, article: Article, missing_article: Article):
    with getTitleRepository(style) as repo:
        repo.set_title(article.title, article)
        actual = repo.get_title(article.title)
        expected = Title.fromArticle(article)
        assert expected == actual

        assume(missing_article.title != article.title)
        actual = repo.get_title(missing_article.title)
        expected = None
        assert expected == actual


@pytest.mark.parametrize('style', styles)
@given(an_article())
def test_should_list_titles(style, article: Article):
    with getTitleRepository(style) as repo:
        repo.set_title(article.title, article)
        titles = list(repo.get_titles())

        assert Title.fromArticle(article) in titles
