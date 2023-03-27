from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sigili.article.repository import ArticleRepository, ArticleUpdate, Article
from sigili.article.repository import MemoryArticleRepository
from sigili.article.repository import FileSystemArticleRepository
from sigili.type.id import ArticleID, ContentID


class ControlArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self.articles = {}
        self.updates = {}

    def _add_article(self, update: ArticleUpdate) -> Article:
        articleId = ArticleID.getArticleID(update)
        contentId = ContentID.getContentID(update.content)
        title = update.title
        newArticle = Article(
            title,
            articleId,
            contentId,
            update.groups,
            update.editOf
        )
        return newArticle

    def add_article(self, update: ArticleUpdate) -> Article:
        newArticle = self._add_article(update)
        self.articles[newArticle.articleId] = newArticle
        self.updates[newArticle.articleId] = update
        return newArticle

    def update_article(self, update: ArticleUpdate) -> Article:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError
        return self.add_article(update)

    def get_article(self, articleId: str) -> Article:
        return self.articles[articleId]

    def has_article(self, articleId: str) -> bool:
        return articleId in self.articles

    def get_articleIds(self) -> set[str]:
        return set(self.articles)

    def get_update(self, articleId: str) -> ArticleUpdate:
        return self.updates[articleId]


@pytest.fixture
def fileRepo(tmp_path):
    _paths = FileSystemArticleRepository.initialize_directory(tmp_path)
    yield FileSystemArticleRepository(_paths)


@pytest.fixture
def memoryRepo():
    yield MemoryArticleRepository()


@pytest.fixture
def simpleRepo():
    yield ControlArticleRepository()


@contextmanager
def getArticleRepository(style: str):
    match style:
        case ControlArticleRepository.__name__:
            yield ControlArticleRepository()
        case MemoryArticleRepository.__name__:
            yield MemoryArticleRepository()
        case FileSystemArticleRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _paths = FileSystemArticleRepository.initialize_directory(_dirPath)
            try:
                yield FileSystemArticleRepository(_paths)
            finally:
                _dir.cleanup()


styles = {
    MemoryArticleRepository.__name__,
    FileSystemArticleRepository.__name__,
    ControlArticleRepository.__name__,
}


@pytest.fixture
def testRepo():
    return ControlArticleRepository()


@pytest.fixture
def testUpdate():
    return ArticleUpdate(
        'Test',
        b'Test',
        ['test']
    )


@pytest.fixture
def testArticle(testRepo, testUpdate):
    return testRepo._add_article(testUpdate)


@pytest.mark.parametrize('style', styles)
def test_does_add_article(style, testRepo):
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(
            'Hello World', b'Hello World', ['hello world'])
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
        articleUpdate = ArticleUpdate(
            'Hello World', b'Hello World', ['hello world'])
        articleDetails = repo.add_article(articleUpdate)
        testRepo.add_article(articleUpdate)

        articleUpdate = ArticleUpdate(
            'Goodnight Moon', b'Goodnight Moon', ['hello world'], articleDetails.articleId)
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
        _testUpdate = ArticleUpdate(
            'Hello World', b'Hello World', ['hello world'])
        articleDetails = repo.merge_article(_testUpdate)
        expectedDetails = testRepo.merge_article(
            _testUpdate)

        assert articleDetails == expectedDetails

        # Update
        _testUpdate = ArticleUpdate(
            'Goodnight Moon', b'Goodnight Moon', ['hello world'], articleDetails.articleId)
        articleDetails = repo.merge_article(_testUpdate)
        expectedDetails = testRepo.merge_article(
            _testUpdate)
        assert articleDetails == expectedDetails
