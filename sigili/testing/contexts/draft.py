
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from sigili.draft.repository import FileSystemDraftRepository, MemoryDraftRepository


@contextmanager
def getDraftRepository(style: str, directory: Path | None = None):
    match style:
        case MemoryDraftRepository.__name__:
            yield MemoryDraftRepository()
        case FileSystemDraftRepository.__name__:
            _dir = None
            if (directory is None):
                _dir = TemporaryDirectory()
                _dirPath = Path(_dir.name)
                directory = FileSystemDraftRepository.initialize_directory(
                    _dirPath)
            try:
                yield FileSystemDraftRepository(directory)
            finally:
                if (_dir is not None):
                    _dir.cleanup()


styles = {
    MemoryDraftRepository.__name__,
    FileSystemDraftRepository.__name__,
}
