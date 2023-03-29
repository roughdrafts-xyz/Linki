
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.title.repository import FileSystemTitleRepository, MemoryTitleRepository


@contextmanager
def getTitleRepository(style: str):
    match style:
        case MemoryTitleRepository.__name__:
            yield MemoryTitleRepository()
        case FileSystemTitleRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _titlePath = FileSystemTitleRepository.initialize_directory(
                _dirPath)
            try:
                yield FileSystemTitleRepository(_titlePath)
            finally:
                _dir.cleanup()


styles = {
    MemoryTitleRepository.__name__,
    FileSystemTitleRepository.__name__,
}
