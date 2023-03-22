from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from sigili.article.content.repository import MemoryContentRepository
from sigili.article.content.repository import FileSystemContentRepository
from sigili.article.content.repository import BadContentRepository


@contextmanager
def getHistoryRepository(style: str):
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


class TestHistoryRepositoryStyles(TestCase):
    styles = {
        MemoryContentRepository.__name__,
        FileSystemContentRepository.__name__,
        # BadArticleRepository.__name__,
    }

    def test_does_add_edit(self):
        for style in self.styles:
            with self.subTest(style=style), getHistoryRepository(style) as repo:
                repo.add_edit(0, 1)

                expected_parent = 0
                expected_child = 1
                actual_parent = repo.get_parent(1)
                actual_child = repo.get_child(1)

                self.assertEqual(expected_parent, actual_parent)
                self.assertEqual(expected_child, actual_child)
