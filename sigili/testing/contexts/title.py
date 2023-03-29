
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.title.repository import FileSystemTitleRepository, MemoryTitleRepository


@contextmanager
def getTitleRepository(style: str, directory: Path | None = None):
    match style:
        case MemoryTitleRepository.__name__:
            yield MemoryTitleRepository()
        case FileSystemTitleRepository.__name__:
            _dir = None
            if (directory is None):
                _dir = TemporaryDirectory()
                _dirPath = Path(_dir.name)
                directory = FileSystemTitleRepository.initialize_directory(
                    _dirPath)
            try:
                yield FileSystemTitleRepository(directory)
            finally:
                if (_dir is not None):
                    _dir.cleanup()


styles = {
    MemoryTitleRepository.__name__,
    FileSystemTitleRepository.__name__,
}
