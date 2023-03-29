
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
            _sigiliPath = _dirPath.joinpath('.sigili')
            _sigiliPath.mkdir()
            _draftPath = FileSystemDraftRepository.initialize_directory(
                _sigiliPath)
            try:
                yield FileSystemDraftRepository(_dirPath, _draftPath)
            finally:
                _dir.cleanup()


styles = {
    MemoryDraftRepository.__name__,
    FileSystemDraftRepository.__name__,
}
