from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sigili.article.content.repository import ContentRepository
from sigili.article.repository import ArticleRepository, ArticleUpdate, ArticleDetails
from sigili.article.repository import MemoryArticleRepository
from sigili.article.repository import FileSystemArticleRepository


class TestArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self.contentId = '0'

    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        self.contentId = ContentRepository.getContentID(
            self.contentId, update.content)
        return ArticleDetails(self.contentId)

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        return self.add_article(update)

    def merge_article(self, update: ArticleUpdate) -> ArticleDetails:
        return self.add_article(update)


@contextmanager
def getArticleRepository(style: str):
    match style:
        case TestArticleRepository.__name__:
            yield TestArticleRepository()
        case MemoryArticleRepository.__name__:
            yield MemoryArticleRepository()
#       case FileSystemArticleRepository.__name__:
#           _dir = TemporaryDirectory()
#           _dirPath = Path(_dir.name)
#           FileSystemArticleRepository.initialize_directory(_dirPath)
#           try:
#               yield FileSystemArticleRepository(path=_dirPath)
#           finally:
#               _dir.cleanup()


styles = {
    MemoryArticleRepository.__name__,
    # FileSystemArticleRepository.__name__,
    TestArticleRepository.__name__,
}

# ArticleUpdate(bytes, [groups]) @dataclass
# ArticleDetails() @dataclass?
# ArticleRepository
#   add_article(ArticleUpdate) -> ArticleDetails
#   update_article(ArticleUpdate) -> ArticleDetails
#   merge_article(ArticleUpdate) -> ArticleDetails
#


@pytest.mark.parametrize('style', styles)
def test_does_add_article(style):
    expectedArticleRepository = TestArticleRepository()
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.add_article(articleUpdate)
        assert articleDetails == expectedArticleRepository.add_article(
            articleUpdate)


@pytest.mark.parametrize('style', styles)
def test_does_update_article(style):
    expectedArticleRepository = TestArticleRepository()
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        repo.add_article(articleUpdate)
        expectedArticleRepository.add_article(articleUpdate)

        articleUpdate = ArticleUpdate(b'Goodnight Moon', ['hello world'])
        articleDetails = repo.update_article(articleUpdate)
        expectedDetails = expectedArticleRepository.update_article(
            articleUpdate)
        assert articleDetails == expectedDetails


@pytest.mark.parametrize('style', styles)
def test_does_merge_article(style):
    expectedArticleRepository = TestArticleRepository()
    with getArticleRepository(style) as repo:
        # Add
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.merge_article(articleUpdate)
        expectedDetails = expectedArticleRepository.merge_article(
            articleUpdate)

        assert articleDetails == expectedDetails

        # Update
        articleUpdate = ArticleUpdate(b'Goodnight Moon', ['hello world'])
        articleDetails = repo.merge_article(articleUpdate)
        expectedDetails = expectedArticleRepository.merge_article(
            articleUpdate)
        assert articleDetails == expectedDetails
