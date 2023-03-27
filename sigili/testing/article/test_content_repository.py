from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.article.content.repository import ContentRepository, MemoryContentRepository
from sigili.article.content.repository import FileSystemContentRepository

import pytest

from sigili.type.id import ContentID


class TestContentRepository(ContentRepository):
    def add_content(self, content: bytes) -> str:
        return ContentID.getContentID(content)

    def get_content(self, contentId: str) -> bytes:
        del contentId
        return b'Hello World'


@contextmanager
def getContentRepository(style: str):
    match style:
        case MemoryContentRepository.__name__:
            yield MemoryContentRepository()
        case TestContentRepository.__name__:
            yield TestContentRepository()
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
    TestContentRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
def test_does_add_and_get_content(style):
    helloWorld = b'Hello World'
    expected = helloWorld
    with getContentRepository(style) as repo:
        refId = repo.add_content(helloWorld)
        actual = repo.get_content(refId)
        assert expected == actual
