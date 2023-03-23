from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sigili.article.content.repository import ContentRepository
from sigili.article.repository import ArticleRepository, ArticleUpdate, ArticleDetails
from sigili.article.repository import MemoryArticleRepository
# from sigili.article.repository import FileSystemArticleRepository


class TestArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self.articles = {}

    def _add_article(self, update: ArticleUpdate) -> ArticleDetails:
        articleId = ContentRepository.getContentID(update.content)
        newArticle = ArticleDetails(
            articleId,
            update.groups,
            update.editOf
        )
        return newArticle

    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        newArticle = self._add_article(update)
        self.articles[newArticle.articleId] = newArticle
        return newArticle

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError
        return self.add_article(update)

    def merge_article(self, update: ArticleUpdate) -> ArticleDetails:
        return self.add_article(update)

    def get_article(self, articleId: str) -> ArticleDetails:
        return self.articles[articleId]

    def has_article(self, articleId: str) -> bool:
        return articleId in self.articles


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
def test_does_not_has_missing_article(style):
    expectedArticleRepository = TestArticleRepository()
    testArticle = expectedArticleRepository._add_article(ArticleUpdate(
        b'Test',
        ['test']
    ))
    with getArticleRepository(style) as repo:
        articleDetails = repo.has_article(testArticle.articleId)
        assert articleDetails == expectedArticleRepository.has_article(
            testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_has_added_article(style):
    expectedArticleRepository = TestArticleRepository()
    testUpdate = ArticleUpdate(
        b'Test',
        ['test']
    )
    testArticle = expectedArticleRepository._add_article(testUpdate)
    with getArticleRepository(style) as repo:
        repo.add_article(testUpdate)
        expectedArticleRepository.add_article(testUpdate)
        articleDetails = repo.has_article(testArticle.articleId)
        assert articleDetails == expectedArticleRepository.has_article(
            testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_not_get_missing_article(style):
    expectedArticleRepository = TestArticleRepository()
    testArticle = expectedArticleRepository._add_article(ArticleUpdate(
        b'Test',
        ['test']
    ))
    with getArticleRepository(style) as repo, pytest.raises(KeyError):
        repo.get_article(testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_get_added_article(style):
    expectedArticleRepository = TestArticleRepository()
    testUpdate = ArticleUpdate(
        b'Test',
        ['test']
    )
    testArticle = expectedArticleRepository._add_article(testUpdate)
    with getArticleRepository(style) as repo:
        repo.add_article(testUpdate)
        expectedArticleRepository.add_article(testUpdate)
        articleDetails = repo.get_article(testArticle.articleId)
        assert articleDetails == expectedArticleRepository.get_article(
            testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_update_article(style):
    expectedArticleRepository = TestArticleRepository()
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.add_article(articleUpdate)
        expectedArticleRepository.add_article(articleUpdate)

        articleUpdate = ArticleUpdate(
            b'Goodnight Moon', ['hello world'], articleDetails.articleId)
        articleDetails = repo.update_article(articleUpdate)
        expectedDetails = expectedArticleRepository.update_article(
            articleUpdate)
        assert articleDetails == expectedDetails


@pytest.mark.parametrize('style', styles)
def test_does_not_update_new_article(style):
    testUpdate = ArticleUpdate(
        b'Test',
        ['test']
    )
    with getArticleRepository(style) as repo, pytest.raises(KeyError):
        repo.update_article(testUpdate)


@pytest.mark.parametrize('style', styles)
def test_does_merge_article(style):
    expectedArticleRepository = TestArticleRepository()
    with getArticleRepository(style) as repo:
        # Add
        testUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.merge_article(testUpdate)
        expectedDetails = expectedArticleRepository.merge_article(
            testUpdate)

        assert articleDetails == expectedDetails

        # Update
        testUpdate = ArticleUpdate(
            b'Goodnight Moon', ['hello world'], articleDetails.articleId)
        articleDetails = repo.merge_article(testUpdate)
        expectedDetails = expectedArticleRepository.merge_article(
            testUpdate)
        assert articleDetails == expectedDetails
