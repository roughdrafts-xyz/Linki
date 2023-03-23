import pytest
from tests.article.test_article_repository import memoryRepo

from sigili.article.repository import ArticleUpdate
from sigili.article.repository import MemoryArticleRepository
from sigili.wiki import Wiki


@pytest.fixture
def otherRepo():
    yield MemoryArticleRepository()


@pytest.fixture
def wiki(memoryRepo, otherRepo):
    yield Wiki({memoryRepo, otherRepo})


def test_does_sync_with_same_history(memoryRepo, otherRepo, wiki):
    expectedLocal = memoryRepo.add_article(
        ArticleUpdate(b'Hello World', []))
    expectedRemote = otherRepo.add_article(
        ArticleUpdate(b'Hello World', []))

    wiki.sync()

    actualLocal = otherRepo.get_article(expectedLocal.articleId)
    actualRemote = memoryRepo.get_article(
        expectedRemote.articleId)

    assert expectedRemote == actualRemote
    assert expectedLocal == actualLocal


def test_does_sync_with_different_history(memoryRepo, otherRepo, wiki):
    expectedLocal = otherRepo.add_article(
        ArticleUpdate(b'Hello Moon', []))
    expectedRemote = memoryRepo.add_article(
        ArticleUpdate(b'Hello Sun', []))

    wiki.sync()

    actualLocal = memoryRepo.get_article(expectedLocal.articleId)
    actualRemote = otherRepo.get_article(
        expectedRemote.articleId)

    assert expectedRemote == actualRemote
    assert expectedLocal == actualLocal


def test_does_sync_with_same_long_history(memoryRepo, otherRepo, wiki):
    helloMoon = ArticleUpdate(b'Hello Moon', [])
    remoteArticleDetails = otherRepo.add_article(helloMoon)
    goodNightMoon = ArticleUpdate(
        b'Goodnight Moon', [], remoteArticleDetails.articleId)
    memoryRepo.add_article(helloMoon)

    otherRepo.update_article(goodNightMoon)
    memoryRepo.update_article(goodNightMoon)

    wiki.sync()

    remoteIds = otherRepo.get_articleIds()
    localIds = memoryRepo.get_articleIds()
    assert sorted(remoteIds) == sorted(localIds)


def test_does_sync_with_different_long_history(memoryRepo, otherRepo, wiki):
    helloMoon = ArticleUpdate(b'Hello Moon', [])
    remoteArticleDetails = otherRepo.add_article(helloMoon)
    goodNightMoon = ArticleUpdate(
        b'Goodnight Moon', [], remoteArticleDetails.articleId)
    helloSun = ArticleUpdate(
        b'Hello Sun', [], remoteArticleDetails.articleId
    )
    memoryRepo.add_article(helloMoon)

    otherRepo.update_article(goodNightMoon)
    memoryRepo.update_article(helloSun)

    wiki.sync()

    remoteIds = otherRepo.get_articleIds()
    localIds = memoryRepo.get_articleIds()
    assert sorted(remoteIds) == sorted(localIds)
