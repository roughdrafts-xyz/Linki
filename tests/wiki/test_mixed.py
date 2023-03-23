import pytest

from tests.article.test_article_repository import fileRepo, memoryRepo
from sigili.article.repository import ArticleUpdate

from sigili.wiki import Wiki


@pytest.fixture
def wiki(memoryRepo, fileRepo):
    yield Wiki({memoryRepo, fileRepo})


def test_does_sync_with_same_history(memoryRepo, fileRepo, wiki):
    expectedLocal = memoryRepo.add_article(
        ArticleUpdate(b'Hello World', []))
    expectedRemote = fileRepo.add_article(
        ArticleUpdate(b'Hello World', []))

    wiki.sync()

    actualLocal = fileRepo.get_article(expectedLocal.articleId)
    actualRemote = memoryRepo.get_article(
        expectedRemote.articleId)

    assert expectedRemote == actualRemote
    assert expectedLocal == actualLocal


def test_does_sync_with_different_history(memoryRepo, fileRepo, wiki):
    expectedLocal = fileRepo.add_article(
        ArticleUpdate(b'Hello Moon', []))
    expectedRemote = memoryRepo.add_article(
        ArticleUpdate(b'Hello Sun', []))

    wiki.sync()

    actualLocal = memoryRepo.get_article(expectedLocal.articleId)
    actualRemote = fileRepo.get_article(
        expectedRemote.articleId)

    assert expectedRemote == actualRemote
    assert expectedLocal == actualLocal


def test_does_sync_with_same_long_history(memoryRepo, fileRepo, wiki):
    helloMoon = ArticleUpdate(b'Hello Moon', [])
    remoteArticleDetails = fileRepo.add_article(helloMoon)
    goodNightMoon = ArticleUpdate(
        b'Goodnight Moon', [], remoteArticleDetails.articleId)
    memoryRepo.add_article(helloMoon)

    fileRepo.update_article(goodNightMoon)
    memoryRepo.update_article(goodNightMoon)

    wiki.sync()

    remoteIds = fileRepo.get_articleIds()
    localIds = memoryRepo.get_articleIds()
    assert sorted(remoteIds) == sorted(localIds)


def test_does_sync_with_different_long_history(memoryRepo, fileRepo, wiki):
    helloMoon = ArticleUpdate(b'Hello Moon', [])
    remoteArticleDetails = fileRepo.add_article(helloMoon)
    goodNightMoon = ArticleUpdate(
        b'Goodnight Moon', [], remoteArticleDetails.articleId)
    helloSun = ArticleUpdate(
        b'Hello Sun', [], remoteArticleDetails.articleId
    )
    memoryRepo.add_article(helloMoon)

    fileRepo.update_article(goodNightMoon)
    memoryRepo.update_article(helloSun)

    wiki.sync()

    remoteIds = fileRepo.get_articleIds()
    localIds = memoryRepo.get_articleIds()
    assert sorted(remoteIds) == sorted(localIds)
