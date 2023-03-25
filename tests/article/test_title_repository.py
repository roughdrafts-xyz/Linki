from contextlib import contextmanager
import pytest
from sigili.article.repository import MemoryArticleRepository

from sigili.title.repository import TitleDetails


# CAR needs to be able to track what the CAs are.
# CAR needs to provide CAs or information about them.

# Titles is the choice of phrase for current titles

@contextmanager
def getTitleRepository(style: str):
    match style:
        case MemoryTitleRepository.__name__:
            yield MemoryTitleRepository()
        case TestTitleRepository.__name__:
            yield TestTitleRepository()
        case FileSystemTitleRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _contentPath = FileSystemTitleRepository.initialize_directory(
                _dirPath)
            try:
                yield FileSystemTitleRepository(path=_contentPath)
            finally:
                _dir.cleanup()


styles = {
    MemoryTitleRepository.__name__,
    FileSystemTitleRepository.__name__,
    TestTitleRepository.__name__,
}


@pytest.fixture
def article_update():
    return ArticleUpdate()


@pytest.mark.parametrize('style', styles)
def test_should_set_current_title():
    with getTitleRepository(style) as repo:
        # titles only have one title, but one title can have multiple titles
        # should handle ignoring a no-op
        current_title_details = repo.set_title(title, articleId)
        assert current_title_details == TitleDetails()

        # should handle a new set
        current_title_details = repo.set_title(title, new_articleId)
        assert current_title_details == TitleDetails()

        # should unset a title
        current_title_details = repo.set_title(title, None)
        assert current_title_details == None


@pytest.mark.parametrize('style', styles)
def test_should_get_options():
    with getTitleRepository(style) as repo:
        # return a list of titles with title
        options = repo.get_options(title)
        assert options == [TitleDetails()]
        pass


@pytest.mark.parametrize('style', styles)
def test_should_get_current_title():
    with getTitleRepository(style) as repo:
        current_title_details = repo.get_title(title)
        assert current_title_details == TitleDetails()
        pass


@pytest.mark.parametrize('style', styles)
def test_should_list_current_titles():
    with getTitleRepository(style) as repo:
        current_titles_details = repo.get_titles()
        assert current_titles_details == [TitleDetails()]
        pass
