from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from sigili.article.repository import Article, ArticleRepository, ArticleUpdate, FileSystemArticleRepository, MemoryArticleRepository
from sigili.type.id import ArticleID, ContentID


class ControlArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self.articles = {}
        self.updates = {}

    def _add_article(self, update: ArticleUpdate) -> Article:
        articleId = ArticleID.getArticleID(update)
        contentId = ContentID.getContentID(update.content)
        title = update.title
        newArticle = Article(
            title,
            articleId,
            contentId,
            update.groups,
            update.editOf
        )
        return newArticle

    def add_article(self, update: ArticleUpdate) -> Article:
        newArticle = self._add_article(update)
        self.articles[newArticle.articleId] = newArticle
        self.updates[newArticle.articleId] = update
        return newArticle

    def update_article(self, update: ArticleUpdate) -> Article:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError
        return self.add_article(update)

    def get_article(self, articleId: str) -> Article:
        return self.articles[articleId]

    def has_article(self, articleId: str) -> bool:
        return articleId in self.articles

    def get_articleIds(self) -> set[str]:
        return set(self.articles)

    def get_update(self, articleId: str) -> ArticleUpdate:
        return self.updates[articleId]


@contextmanager
def getArticleRepository(style: str):
    match style:
        case ControlArticleRepository.__name__:
            yield ControlArticleRepository()
        case MemoryArticleRepository.__name__:
            yield MemoryArticleRepository()
        case FileSystemArticleRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _paths = FileSystemArticleRepository.initialize_directory(_dirPath)
            try:
                yield FileSystemArticleRepository(_paths)
            finally:
                _dir.cleanup()


styles = {
    MemoryArticleRepository.__name__,
    FileSystemArticleRepository.__name__,
    ControlArticleRepository.__name__,
}
