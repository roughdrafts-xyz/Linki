from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.article.history.repository import MemoryHistoryRepository

import pytest


@contextmanager
def getHistoryRepository(style: str):
    match style:
        case MemoryHistoryRepository.__name__:
            yield MemoryHistoryRepository()
        case BadHistoryRepository.__name__:
            yield BadHistoryRepository()
        case FileSystemHistoryRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            FileSystemHistoryRepository.initialize_directory(_dirPath)
            try:
                yield FileSystemHistoryRepository(path=_dirPath)
            finally:
                _dir.cleanup()


styles = {
    MemoryHistoryRepository.__name__,
    # FileSystemHistoryRepository.__name__,
    # BadArticleRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
def test_does_add_edit(style):
    with getHistoryRepository(style) as repo:
        parent = 'a'
        child = 'b'
        repo.add_edit(parent, child)

        expected_parent = parent
        expected_children = [child]
        actual_parent = repo.get_parent(child)
        actual_children = repo.get_children(parent)

        assert expected_parent == actual_parent
        assert expected_children == actual_children
