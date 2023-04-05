import pytest
from sigili.article.repository import Article, ArticleUpdate
from sigili.article.repository import MemoryArticleRepository
from sigili.article.repository import FileSystemArticleRepository
from sigili.testing.contexts.article import ControlArticleRepository, getArticleRepository, styles
from sigili.type.id import Label


@pytest.fixture
def fileRepo(tmp_path):
    _paths = FileSystemArticleRepository.init(tmp_path)
    yield FileSystemArticleRepository(_paths)


@pytest.fixture
def memoryRepo():
    yield MemoryArticleRepository()


@pytest.fixture
def simpleRepo():
    yield ControlArticleRepository()


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
def anotherUpdate():
    return ArticleUpdate('Hello World', b'Hello World', ['hello world'])


@pytest.fixture
def testArticle(testUpdate):
    return Article.fromArticleUpdate(testUpdate)


@pytest.mark.parametrize('style', styles)
def test_does_add_article(style, testRepo, anotherUpdate):
    with getArticleRepository(style) as repo:
        articleDetails = repo.add_article(anotherUpdate)
        assert articleDetails == testRepo.add_article(
            anotherUpdate)


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
        added = repo.add_article(testUpdate)
        testAdded = testRepo.add_article(testUpdate)
        assert added == testAdded
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
