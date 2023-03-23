from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sigili.article.content.repository import ContentRepository
from sigili.article.repository import ArticleRepository, ArticleUpdate, ArticleDetails
# from sigili.article.repository import MemoryArticleRepository
# from sigili.article.repository import FileSystemArticleRepository


class TestArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self.articles = {}
        self.updates = {}

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
        self.updates[newArticle.articleId] = update
        return newArticle

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError
        return self.add_article(update)

    def get_article(self, articleId: str) -> ArticleDetails:
        return self.articles[articleId]

    def has_article(self, articleId: str) -> bool:
        return articleId in self.articles

    def get_articleIds(self) -> set[str]:
        return set(self.articles)

    def get_update(self, articleId: str) -> ArticleUpdate:
        return self.updates[articleId]


@contextmanager
def getArticleRepository(style: str):
    match style:
        case TestArticleRepository.__name__:
            yield TestArticleRepository()
#       case MemoryArticleRepository.__name__:
#           yield MemoryArticleRepository()
#       case FileSystemArticleRepository.__name__:
#           _dir = TemporaryDirectory()
#           _dirPath = Path(_dir.name)
#           _paths = FileSystemArticleRepository.initialize_directory(_dirPath)
#           try:
#               yield FileSystemArticleRepository(_paths)
#           finally:
#               _dir.cleanup()


styles = {
    #   MemoryArticleRepository.__name__,
    #   FileSystemArticleRepository.__name__,
    TestArticleRepository.__name__,
}


@pytest.fixture
def testRepo():
    return TestArticleRepository()


@pytest.fixture
def testUpdate():
    return ArticleUpdate(
        b'Test',
        ['test']
    )


@pytest.fixture
def testArticle(testRepo, testUpdate):
    return testRepo._add_article(testUpdate)


@pytest.mark.parametrize('style', styles)
def test_does_add_article(style, testRepo):
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.add_article(articleUpdate)
        assert articleDetails == testRepo.add_article(
            articleUpdate)


@pytest.mark.parametrize('style', styles)
def test_does_not_has_missing_article(style, testRepo, testArticle):
    with getArticleRepository(style) as repo:
        articleDetails = repo.has_article(testArticle.articleId)
        assert articleDetails == testRepo.has_article(
            testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_has_added_article(style, testUpdate, testArticle, testRepo):
    with getArticleRepository(style) as repo:
        repo.add_article(testUpdate)
        testRepo.add_article(testUpdate)
        articleDetails = repo.has_article(testArticle.articleId)
        assert articleDetails == testRepo.has_article(
            testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_not_get_missing_article(style, testArticle):
    with getArticleRepository(style) as repo, pytest.raises(KeyError):
        repo.get_article(testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_get_added_article(style, testUpdate, testArticle, testRepo):
    with getArticleRepository(style) as repo:
        repo.add_article(testUpdate)
        testRepo.add_article(testUpdate)
        articleDetails = repo.get_article(testArticle.articleId)
        assert articleDetails == testRepo.get_article(
            testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_not_get_missing_update(style, testArticle):
    with getArticleRepository(style) as repo, pytest.raises(KeyError):
        repo.get_update(testArticle.articleId)


@pytest.mark.parametrize('style', styles)
def test_does_get_existing_update(style, testUpdate, testRepo, testArticle):
    with getArticleRepository(style) as repo:
        repo.add_article(testUpdate)
        testRepo.add_article(testUpdate)
        expectedUpdate = testRepo.get_update(
            testArticle.articleId)
        actualUpdate = repo.get_update(testArticle.articleId)
        assert actualUpdate == expectedUpdate


@pytest.mark.parametrize('style', styles)
def test_does_get_article_ids_from_empty(style, testRepo):
    with getArticleRepository(style) as repo:
        expectedArticleIds = testRepo.get_articleIds()
        actualArticleIds = repo.get_articleIds()

        assert expectedArticleIds == actualArticleIds


@pytest.mark.parametrize('style', styles)
def test_does_get_article_ids_from_filled(style, testUpdate, testRepo):
    with getArticleRepository(style) as repo:
        repo.add_article(testUpdate)
        testRepo.add_article(testUpdate)
        expectedArticleIds = testRepo.get_articleIds()
        actualArticleIds = repo.get_articleIds()

        assert expectedArticleIds == actualArticleIds


@pytest.mark.parametrize('style', styles)
def test_does_update_article(style, testRepo):
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.add_article(articleUpdate)
        testRepo.add_article(articleUpdate)

        articleUpdate = ArticleUpdate(
            b'Goodnight Moon', ['hello world'], articleDetails.articleId)
        articleDetails = repo.update_article(articleUpdate)
        expectedDetails = testRepo.update_article(
            articleUpdate)
        assert articleDetails == expectedDetails


@pytest.mark.parametrize('style', styles)
def test_does_not_update_new_article(style, testUpdate):
    with getArticleRepository(style) as repo, pytest.raises(KeyError):
        repo.update_article(testUpdate)


@pytest.mark.parametrize('style', styles)
def test_does_merge_article(style, testRepo):
    with getArticleRepository(style) as repo:
        # Add
        _testUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.merge_article(_testUpdate)
        expectedDetails = testRepo.merge_article(
            _testUpdate)

        assert articleDetails == expectedDetails

        # Update
        _testUpdate = ArticleUpdate(
            b'Goodnight Moon', ['hello world'], articleDetails.articleId)
        articleDetails = repo.merge_article(_testUpdate)
        expectedDetails = testRepo.merge_article(
            _testUpdate)
        assert articleDetails == expectedDetails
