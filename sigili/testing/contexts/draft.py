
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from sigili.draft.repository import FileSystemDraftRepository, MemoryDraftRepository


@contextmanager
def getDraftRepository(style: str):
    match style:
        case MemoryDraftRepository.__name__:
            yield MemoryDraftRepository()
        case FileSystemDraftRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _draftPath = FileSystemDraftRepository.initialize_directory(
                _dirPath)
            try:
                yield FileSystemDraftRepository(_draftPath)
            finally:
                _dir.cleanup()


styles = {
    MemoryDraftRepository.__name__,
    FileSystemDraftRepository.__name__,
}
