from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
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
    MemoryArticleRepository.__name__,
    FileSystemArticleRepository.__name__,
    # BadArticleRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
def test_does_update_articles(style):
    with getArticleRepository(style) as repo:
        pass
