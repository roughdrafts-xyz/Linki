from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from sigili.article.content.repository import MemoryContentRepository
from sigili.article.content.repository import FileSystemContentRepository
from sigili.article.content.repository import BadContentRepository
from sigili.data.ref import RefDetail


@contextmanager
def getRepository(style: str):
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


class TestArticleRepositoryStyles(TestCase):
    styles = {
        MemoryContentRepository.__name__,
        FileSystemContentRepository.__name__,
        # BadArticleRepository.__name__,
    }
