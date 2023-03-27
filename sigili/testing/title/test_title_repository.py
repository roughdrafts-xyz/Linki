from contextlib import contextmanager
from typing import Iterable, List
from unittest import TestCase
from hypothesis import given, strategies
import pytest
from sigili.article.repository import Article, ArticleUpdate, MemoryArticleRepository
from sigili.draft.repository import Draft
from sigili.testing.strategies.article import some_articles
from sigili.testing.strategies.draft import a_draft, a_drafted_article_update, some_drafts

from sigili.title.repository import MemoryTitleRepository

# from sigili.title.repository import TitleDetails


# CAR needs to be able to track what the CAs are.
# CAR needs to provide CAs or information about them.

# Titles is the choice of phrase for current titles


@contextmanager
def getTitleRepository(style: str):
    articles = MemoryArticleRepository()
    match style:
        case MemoryTitleRepository.__name__:
            yield MemoryTitleRepository(articles)
#       case FileSystemTitleRepository.__name__:
#           _dir = TemporaryDirectory()
#           _dirPath = Path(_dir.name)
#           _contentPath = FileSystemTitleRepository.initialize_directory(
#               _dirPath)
#           try:
#               yield FileSystemTitleRepository(path=_contentPath)
#           finally:
#               _dir.cleanup()


styles = {
    MemoryTitleRepository.__name__,
    #   FileSystemTitleRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
@given(strategies.data())
def test_should_set_current_title(style, data):
    with getTitleRepository(style) as repo:
        # titles only have one title, but one title can have multiple titles
        # should handle ignoring a no-op
        draft: ArticleUpdate = data.draw(a_drafted_article_update())
        article = Article.fromArticleUpdate(draft)
        current_title = repo.set_title(draft.title, draft)
        assert current_title == article

        # should handle a new set
        draft: ArticleUpdate = data.draw(a_drafted_article_update())
        article = Article.fromArticleUpdate(draft)
        current_title = repo.set_title(draft.title, draft)
        assert current_title == article
        assert current_title != None

        # should handle a an existing title
        draft: ArticleUpdate = data.draw(a_drafted_article_update())
        draft.title = current_title.title
        article = Article.fromArticleUpdate(draft)
        current_title = repo.set_title(draft.title, draft)
        assert current_title == article
        assert current_title != None

        # should unset a title
        current_title = repo.clear_title(current_title.title)
        assert current_title == None


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_get_options(style, draft: Draft):
    with getTitleRepository(style) as repo:
        repo.set_title(draft.title, draft.asArticleUpdate())
        options = repo.get_options(draft.title)
        article = Article.fromArticleUpdate(draft.asArticleUpdate())
        assert article in options


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_get_title(style, draft: Draft):
    with getTitleRepository(style) as repo:
        repo.set_title(draft.title, draft.asArticleUpdate())
        expected = Article.fromArticleUpdate(draft.asArticleUpdate())
        actual = repo.get_title(draft.title)
        assert expected == actual


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_list_titles(style, draft: Draft):
    with getTitleRepository(style) as repo:
        repo.set_title(draft.title, draft.asArticleUpdate())
        article = Article.fromArticleUpdate(draft.asArticleUpdate())
        titles = repo.get_titles()

        assert article in titles
