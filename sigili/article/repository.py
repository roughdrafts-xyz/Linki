from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import json
from pathlib import Path

from sigili.article.content.repository import FileSystemContentRepository, MemoryContentRepository
from sigili.article.group.repository import FileSystemGroupRepository, MemoryGroupRepository
from sigili.article.history.repository import FileSystemHistoryRepository, MemoryHistoryRepository


@dataclass
class ArticleUpdate():
    content: bytes
    groups: list[str]
    editOf: str | None = None


@dataclass
class ArticleDetails():
    articleId: str
    groups: list[str]
    editOf: str | None = None


class ArticleRepository(ABC):
    @abstractmethod
    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        raise NotImplementedError

    @abstractmethod
    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        raise NotImplementedError

    @abstractmethod
    def get_article(self, articleId: str) -> ArticleDetails:
        raise NotImplementedError

    @abstractmethod
    def has_article(self, articleId: str | None) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_articleIds(self) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    def get_update(self, articleId: str) -> ArticleUpdate:
        raise NotImplementedError

    def merge_article(self, update: ArticleUpdate) -> ArticleDetails:
        if (self.has_article(update.editOf)):
            return self.update_article(update)
        return self.add_article(update)


class MemoryArticleRepository(ArticleRepository):
    def __init__(self) -> None:
        self._articles = {}
        self._content = MemoryContentRepository()
        self._history = MemoryHistoryRepository()
        self._groups = MemoryGroupRepository()

    def _add_article(self, update: ArticleUpdate) -> ArticleDetails:
        _content = update.content
        _groups = update.groups

        _contentId = self._content.add_content(_content)
        for group in _groups:
            self._groups.add_to_group(_contentId, group)

        return ArticleDetails(
            articleId=_contentId,
            groups=_groups
        )

    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        newArticle = self._add_article(update)
        self._articles[newArticle.articleId] = newArticle
        return newArticle

    def get_article(self, articleId: str) -> ArticleDetails:
        if (self.has_article(articleId)):
            return self._articles[articleId]
        raise KeyError(
            'Article not found. Try using merge_article or add_article first.')

    def has_article(self, articleId: str | None) -> bool:
        return articleId in self._articles

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError(
                'Article must be an edit of another Article already in the Repository. Try using merge_article or add_article instead.')

        newArticle = self._add_article(update)
        newArticle.editOf = update.editOf
        self._history.add_edit(newArticle.editOf, newArticle.articleId)
        self._articles[newArticle.articleId] = newArticle

        return newArticle

    def get_articleIds(self) -> set[str]:
        return set(self._articles)

    def get_update(self, articleId: str) -> ArticleUpdate:
        _content = self._content.get_content(articleId)
        _article = self._articles[articleId]
        return ArticleUpdate(
            _content,
            _article.groups,
            _article.editOf
        )


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, paths: dict[str, Path]):
        if (not paths['articles'].exists()):
            raise FileNotFoundError(
                f'Articles folder not found in repository. The folder might not be initialized.')

        self._articles = paths['articles']
        self._content = FileSystemContentRepository(paths['content'])
        self._history = FileSystemHistoryRepository(paths['history'])
        self._groups = FileSystemGroupRepository(paths['groups'])

    @staticmethod
    def get_paths(path: Path) -> dict[str, Path]:
        return {
            'articles': path.joinpath('articles').resolve(),
            'content': path.joinpath('content').resolve(),
            'history': path.joinpath('history').resolve(),
            'groups': path.joinpath('groups').resolve()
        }

    @classmethod
    def initialize_directory(cls, path: Path) -> dict[str, Path]:
        if (not path.exists()):
            raise FileNotFoundError
        path_is_not_empty = any(path.iterdir())
        if (path_is_not_empty):
            raise FileExistsError
        _articlePath = path.joinpath('articles')
        _articlePath.mkdir()
        FileSystemContentRepository.initialize_directory(path)
        FileSystemHistoryRepository.initialize_directory(path)
        FileSystemGroupRepository.initialize_directory(path)
        return cls.get_paths(path)

    def _add_article(self, update: ArticleUpdate) -> ArticleDetails:
        _content = update.content
        _groups = update.groups

        _contentId = self._content.add_content(_content)
        for group in _groups:
            self._groups.add_to_group(_contentId, group)

        return ArticleDetails(
            articleId=_contentId,
            groups=_groups
        )

    def _write_article(self, article: ArticleDetails) -> None:
        with self._articles.joinpath(article.articleId).open('w') as _jsonPath:
            json.dump(asdict(article), _jsonPath)

    def _get_article(self, articleId: str) -> ArticleDetails:
        with self._articles.joinpath(articleId).open() as _jsonPath:
            _json = json.load(_jsonPath)
            return ArticleDetails(
                _json['articleId'],
                _json['groups'],
                _json['editOf']
            )

    def add_article(self, update: ArticleUpdate) -> ArticleDetails:
        newArticle = self._add_article(update)
        self._write_article(newArticle)
        return newArticle

    def get_article(self, articleId: str) -> ArticleDetails:
        if (self.has_article(articleId)):
            return self._get_article(articleId)
        raise KeyError(
            'Article not found. Try using merge_article or add_article first.')

    def has_article(self, articleId: str | None) -> bool:
        if (articleId is None):
            return False
        return self._articles.joinpath(articleId).exists()

    def update_article(self, update: ArticleUpdate) -> ArticleDetails:
        if (update.editOf is None or not self.has_article(update.editOf)):
            raise KeyError(
                'Article must be an edit of another Article already in the Repository. Try using merge_article or add_article instead.')

        newArticle = self._add_article(update)
        newArticle.editOf = update.editOf
        self._history.add_edit(newArticle.editOf, newArticle.articleId)
        self._write_article(newArticle)

        return newArticle

    def get_articleIds(self) -> set[str]:
        return {_articles.name for _articles in self._articles.iterdir()}

    def get_update(self, articleId: str) -> ArticleUpdate:
        _article = self.get_article(articleId)
        _content = self._content.get_content(articleId)
        return ArticleUpdate(
            _content,
            _article.groups,
            _article.editOf
        )
