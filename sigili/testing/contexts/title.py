
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.article.repository import ArticleRepository, MemoryArticleRepository

from sigili.title.repository import FileSystemTitleRepository, MemoryTitleRepository


@contextmanager
def getTitleRepository(style: str, articles: ArticleRepository | None = None):
    if (articles is None):
        articles = MemoryArticleRepository()
    match style:
        case MemoryTitleRepository.__name__:
            yield MemoryTitleRepository(articles)
        case FileSystemTitleRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _titlePath = FileSystemTitleRepository.initialize_directory(
                _dirPath)
            try:
                yield FileSystemTitleRepository(articles, _titlePath)
            finally:
                _dir.cleanup()


styles = {
    MemoryTitleRepository.__name__,
    FileSystemTitleRepository.__name__,
}
