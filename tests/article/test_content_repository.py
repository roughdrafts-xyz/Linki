from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from sigili.article.content.repository import MemoryContentRepository
from sigili.article.content.repository import FileSystemContentRepository
from sigili.article.content.repository import BadContentRepository


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
            FileSystemContentRepository.initialize_directory(_dirPath)
            try:
                yield FileSystemContentRepository(path=_dirPath)
            finally:
                _dir.cleanup()


class TestContentRepositoryStyles(TestCase):
    styles = {
        MemoryContentRepository.__name__,
        FileSystemContentRepository.__name__,
        # BadArticleDataRepository.__name__,
    }

    def test_does_add_and_get_content(self):
        helloWorld = b'Hello World'
        expected = helloWorld
        for style in self.styles:
            with self.subTest(style=style), getContentRepository(style) as repo:
                refId = repo.add_content(helloWorld)
                actual = repo.get_content(refId)
                self.assertEqual(expected, actual)