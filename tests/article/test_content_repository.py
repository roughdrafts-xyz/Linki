from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.article.content.repository import MemoryContentRepository
from sigili.article.content.repository import FileSystemContentRepository
from sigili.article.content.repository import BadContentRepository

import pytest


@contextmanager
def getContentRepository(style: str):
    match style:
        case MemoryContentRepository.__name__:
            yield MemoryContentRepository()
        case BadContentRepository.__name__:
            yield BadContentRepository()
        case FileSystemContentRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _contentPath = FileSystemContentRepository.initialize_directory(
                _dirPath)
            try:
                yield FileSystemContentRepository(path=_contentPath)
            finally:
                _dir.cleanup()


styles = {
    MemoryContentRepository.__name__,
    FileSystemContentRepository.__name__,
    # BadContentRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
def test_does_add_and_get_content(style):
    helloWorld = b'Hello World'
    expected = helloWorld
    with getContentRepository(style) as repo:
        refId = repo.add_content(helloWorld)
        actual = repo.get_content(refId)
        assert expected == actual
