from contextlib import contextmanager
from dataclasses import dataclass
import pytest

# from sigili.title.repository import TitleDetails


# CAR needs to be able to track what the CAs are.
# CAR needs to provide CAs or information about them.

# Titles is the choice of phrase for current titles
@dataclass
class TitleDetails:
    title: str
    articleId: str


class MemoryTitleRepository():
    def __init__(self) -> None:
        self.titles: dict[str, TitleDetails] = dict()
        self.store: dict[str, list[TitleDetails]] = dict()

    def set_title(self, title: str, articleId: str | None) -> TitleDetails | None:
        if (articleId is None):
            del self.titles[title]
            return None

        _title_detail = TitleDetails(
            title,
            articleId
        )

        if (title not in self.store):
            self.store[title] = []
        self.store[title].append(_title_detail)
        self.titles[title] = _title_detail
        return _title_detail

    def get_title(self, title) -> TitleDetails:
        return self.titles[title]

    def get_titles(self) -> list[TitleDetails]:
        return list(self.titles.values())

    def get_options(self, title) -> list[TitleDetails]:
        return list(self.store[title])


@contextmanager
def getTitleRepository(style: str):
    match style:
        case MemoryTitleRepository.__name__:
            yield MemoryTitleRepository()
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
def test_should_set_current_title(style):
    with getTitleRepository(style) as repo:
        # titles only have one title, but one title can have multiple titles
        # should handle ignoring a no-op
        title = "Chegg"
        articleId = "12345"
        current_title_details = repo.set_title(title, articleId)
        assert current_title_details == TitleDetails(title, articleId)

        # should handle a new set
        title = "Crugg"
        articleId = "2345"
        current_title_details = repo.set_title(title, articleId)
        assert current_title_details == TitleDetails(title, articleId)

        # should handle a an existing id
        title = "Grugg"
        articleId = "12345"
        current_title_details = repo.set_title(title, articleId)
        assert current_title_details == TitleDetails(title, articleId)

        # should handle a an existing id
        title = "Grugg"
        articleId = "798"
        current_title_details = repo.set_title(title, articleId)
        assert current_title_details == TitleDetails(title, articleId)

        # should handle a an existing title and id
        title = "Crugg"
        articleId = "12345"
        current_title_details = repo.set_title(title, articleId)
        assert current_title_details == TitleDetails(title, articleId)

        # should unset a title
        current_title_details = repo.set_title(title, None)
        assert current_title_details == None


@pytest.mark.parametrize('style', styles)
def test_should_get_options(style):
    with getTitleRepository(style) as repo:
        # return a list of titles with title
        options = repo.get_options(title)
        assert options == [TitleDetails()]
        pass


@pytest.mark.parametrize('style', styles)
def test_should_get_current_title(style):
    with getTitleRepository(style) as repo:
        current_title_details = repo.get_title(title)
        assert current_title_details == TitleDetails()
        pass


@pytest.mark.parametrize('style', styles)
def test_should_list_current_titles(style):
    with getTitleRepository(style) as repo:
        current_titles_details = repo.get_titles()
        assert current_titles_details == [TitleDetails()]
        pass
