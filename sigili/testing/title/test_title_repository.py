from contextlib import contextmanager
from unittest import TestCase
from hypothesis import given, strategies
import pytest
from sigili.article.repository import Article, MemoryArticleRepository
from sigili.testing.article.strategies import an_article, some_articles

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
@given(some_articles(4))
def test_should_set_current_title(style, articles: list[Article]):
    with getTitleRepository(style) as repo:
        # titles only have one title, but one title can have multiple titles
        # should handle ignoring a no-op
        article = articles[0]
        current_title = repo.set_title(article.title, article)
        assert current_title == article

        # should handle a new set
        article = articles[1]
        current_title = repo.set_title(article.title, article)
        assert current_title == article
        assert current_title != None

        # should handle a an existing title
        article = articles[2]
        article.title = current_title.title
        current_title = repo.set_title(article.title, article)
        assert current_title == article
        assert current_title != None

        # should handle a an existing id
        article = articles[2]
        article.title = current_title.articleId
        current_title = repo.set_title(article.title, article)
        assert current_title == article
        assert current_title != None

        # should handle a an existing title and id
        article = articles[2]
        current_title = repo.set_title(article.title, article)
        assert current_title == article
        assert current_title != None

        # should unset a title
        current_title = repo.set_title(current_title.title, None)
        assert current_title == None


#   @pytest.mark.parametrize('style', styles)
#   def test_should_get_options(style):
#       with getTitleRepository(style) as repo:
#           # return a list of titles with title
#           title = "Chegg"
#           articleId = "12345"
#           repo.set_title(title, articleId)
#           title = "Clorg"
#           articleId = "12345"
#           repo.set_title(title, articleId)

#           options = repo.get_options(title)
#           assert options == [Title(title, articleId)]


#   @pytest.mark.parametrize('style', styles)
#   def test_should_get_current_title(style):
#       with getTitleRepository(style) as repo:
#           title = "Chegg"
#           articleId = "12345"
#           repo.set_title(title, articleId)
#           title = "Clorg"
#           articleId = "12345"
#           repo.set_title(title, articleId)

#           current_title_details = repo.get_title(title)
#           assert current_title_details == Title(title, articleId)


#   @pytest.mark.parametrize('style', styles)
#   def test_should_list_current_titles(style):
#       with getTitleRepository(style) as repo:
#           title = "Chegg"
#           articleId = "12345"
#           repo.set_title(title, articleId)
#           _title = "Clorg"
#           _articleId = "12345"
#           repo.set_title(_title, _articleId)

#           current_titles_details = repo.get_titles()

#           test_case = TestCase()
#           test_case.assertCountEqual(current_titles_details, [
#               Title(title, articleId),
#               Title(_title, _articleId)
#           ])


#   st_title = st.tuples(st.text(), st.text())


#   @given(st_title, st_title)
#   @pytest.mark.parametrize('style', styles)
#   @pytest.mark.skip(reason="Not focusing on safety and optimization yet.")
#   def test_should_list_current_titles_hard(style, title1, title2):
#       with getTitleRepository(style) as repo:
#           repo.set_title(*title1)
#           repo.set_title(*title2)

#           current_titles_details = repo.get_titles()

#           test_case = TestCase()
#           test_case.assertCountEqual(current_titles_details, [
#               Title(*title1),
#               Title(*title2)
#           ])
