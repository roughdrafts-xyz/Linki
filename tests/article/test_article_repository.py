from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sigili.article.repository import ArticleUpdate, ArticleDetails
from sigili.article.repository import MemoryArticleRepository
from sigili.article.repository import FileSystemArticleRepository
from sigili.article.repository import BadArticleRepository


@contextmanager
def getArticleRepository(style: str):
    match style:
        case MemoryArticleRepository.__name__:
            yield MemoryArticleRepository()
        case BadArticleRepository.__name__:
            yield BadArticleRepository()
        case FileSystemArticleRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            FileSystemArticleRepository.initialize_directory(_dirPath)
            try:
                yield FileSystemArticleRepository(path=_dirPath)
            finally:
                _dir.cleanup()


styles = {
    # MemoryArticleRepository.__name__,
    # FileSystemArticleRepository.__name__,
    BadArticleRepository.__name__,
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
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.add_article(articleUpdate)
        assert articleDetails == ArticleDetails(
            articleId='1'
        )


@pytest.mark.parametrize('style', styles)
def test_does_update_article(style):
    with getArticleRepository(style) as repo:
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        repo.add_article(articleUpdate)
        articleUpdate = ArticleUpdate(b'Goodnight Moon', ['hello world'])
        articleDetails = repo.update_article(articleUpdate)
        assert articleDetails == ArticleDetails(
            articleId='1'
        )


@pytest.mark.parametrize('style', styles)
def test_does_merge_article(style):
    with getArticleRepository(style) as repo:
        # Add
        articleUpdate = ArticleUpdate(b'Hello World', ['hello world'])
        articleDetails = repo.merge_article(articleUpdate)
        assert articleDetails == ArticleDetails(
            articleId='1'
        )

        # Update
        articleUpdate = ArticleUpdate(b'Goodnight Moon', ['hello world'])
        articleDetails = repo.merge_article(articleUpdate)
        assert articleDetails == ArticleDetails(
            articleId='1'
        )
