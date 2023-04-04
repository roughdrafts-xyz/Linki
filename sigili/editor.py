from pathlib import Path
from typing import Iterable
from sigili.article.repository import ArticleRepository, ArticleUpdate, FileSystemArticleRepository
from sigili.draft.repository import Draft, DraftRepository, FileSystemDraftRepository
from sigili.title.repository import FileSystemTitleRepository, TitleRepository


class Editor():

    def __init__(self, titles: TitleRepository, drafts: DraftRepository, articles: ArticleRepository) -> None:
        self._titles = titles
        self._drafts = drafts
        self._articles = articles

    def get_updates(self) -> Iterable[Draft]:
        for _draft in self._drafts.get_drafts():
            if (_draft.should_update()):
                yield _draft

    def publish_drafts(self) -> int:
        for title in self._titles.get_titles():
            isClear = self._drafts.get_draft(title.title) is None
            if isClear:
                self._titles.clear_title(title.title)

        count = 0
        for draft in self.get_updates():
            count += 1
            article = self._articles.merge_article(draft.asArticleUpdate())
            self._titles.set_title(article.title, article)
        return count

    def load_titles(self) -> None:
        for title in self._titles.get_titles():
            content = self._articles.content.get_content(
                title.contentId)
            draft = Draft(
                title.title,
                content,
                title.groups,
                title
            )
            self._drafts.set_draft(draft)


class FileEditor(Editor):

    @staticmethod
    def init(path: Path):
        _path = path.joinpath('.sigili')
        _path.mkdir()
        FileSystemArticleRepository.init(_path)
        FileSystemTitleRepository.init(_path)
        FileSystemDraftRepository.init(_path)

    @staticmethod
    def fromPath(path: Path):
        _path = path.joinpath('.sigili')
        titles = FileSystemTitleRepository(_path)
        drafts = FileSystemDraftRepository(_path)
        a_paths = FileSystemArticleRepository.get_paths(_path)
        articles = FileSystemArticleRepository(a_paths)
        return Editor(titles, drafts, articles)
