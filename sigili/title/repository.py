from abc import ABC, abstractmethod
from pathlib import Path
import pickle
from typing import Iterator
from sigili.article.repository import Article

from sigili.type.id import ArticleID, Label, LabelID


class Title(Article):
    @classmethod
    def fromArticle(cls, article: Article) -> 'Title':
        return cls(
            article.title,
            article.articleId,
            article.contentId,
            article.groups,
            article.editOf
        )
    pass


class TitleRepository(ABC):
    @abstractmethod
    def set_title(self, title: Label, article: Article) -> Title | None:
        raise NotImplementedError

    @abstractmethod
    def get_title(self, title: Label) -> Title | None:
        raise NotImplementedError

    @abstractmethod
    def clear_title(self, title: Label) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_titles(self) -> Iterator[Title]:
        raise NotImplementedError

# TODO DEPRICATED - Create an Article.from_title(Title|Iterator[Title]) instead.
#   def get_options(self, title: Label) -> Iterator[Article]:
#       for articleId in self.articles.get_articleIds():
#           article = self.articles.get_article(articleId)
#           if (article.title == title):
#               yield article


class MemoryTitleRepository(TitleRepository):
    def __init__(self) -> None:
        self.titles: dict[LabelID, Title] = dict()

    def set_title(self, title: Label, article: Article) -> Title | None:
        new_title = Title.fromArticle(article)
        self.titles[title.labelId] = new_title
        return new_title

    def get_title(self, title: Label) -> Title | None:
        if (title.labelId not in self.titles):
            return None
        return self.titles[title.labelId]

    def get_titles(self) -> Iterator[Title]:
        return self.titles.values().__iter__()

    def clear_title(self, title: Label) -> None:
        if (title.labelId in self.titles):
            del self.titles[title.labelId]


class FileSystemTitleRepository(TitleRepository):
    def __init__(self, path: Path) -> None:
        self._titles = path.resolve()

    @staticmethod
    def init(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _titlePath = path.joinpath('titles')
        _titlePath.mkdir()
        return _titlePath.resolve()

    def set_title(self, title: Label, article: Article) -> Title | None:
        new_title = Title.fromArticle(article)
        with self._titles.joinpath(title.name).open('wb') as _path:
            pickle.dump(new_title, _path)
        return new_title

    def get_title(self, title: Label) -> Title | None:
        _title = self._titles.joinpath(title.name)
        if (not _title.exists()):
            return None
        with _title.open('rb') as _path:
            new_title = pickle.load(_path)
            return new_title

    def clear_title(self, title: Label) -> None:
        _title = self._titles.joinpath(title.name)
        if (not _title.exists()):
            return None
        _title.unlink()

    def get_titles(self) -> Iterator[Title]:
        for title in self._titles.iterdir():
            _label = Label(title.name)
            _title = self.get_title(_label)
            if (_title is not None):
                yield _title
