from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.article.history.repository import FileSystemHistoryRepository, MemoryHistoryRepository

import pytest


@contextmanager
def getHistoryRepository(style: str, directory: Path | None = None):
    match style:
        case MemoryHistoryRepository.__name__:
            yield MemoryHistoryRepository()
        case FileSystemHistoryRepository.__name__:
            _dir = None
            if (directory is None):
                _dir = TemporaryDirectory()
                directory = Path(_dir.name)
                directory = FileSystemHistoryRepository.initialize_directory(
                    directory)
            try:
                yield FileSystemHistoryRepository(path=directory)
            finally:
                if (_dir is not None):
                    _dir.cleanup()


styles = {
    MemoryHistoryRepository.__name__,
    FileSystemHistoryRepository.__name__,
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
