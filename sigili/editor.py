from glob import iglob
from pathlib import Path
from typing import Iterable
from sigili.article.repository import ArticleRepository, ArticleUpdate, FileSystemArticleRepository
from sigili.draft.repository import Draft, DraftRepository, FileSystemDraftRepository
from sigili.title.repository import FileSystemTitleRepository, TitleRepository
from sigili.type.id import Label


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

    def copy_articles(self, articles: ArticleRepository):
        # TODO Make a dataclass of ArticleCollection that simplifies this?

        count = 0
        for article_id in articles.get_articleIds():
            if (self._articles.has_article(article_id)):
                continue
            article = articles.get_article(article_id)
            content = articles.content.get_content(article.contentId)
            update = ArticleUpdate.createUpdate(article, content)
            self._articles.merge_article(update)
            count += 1
        return count

    def copy_titles(self, titles: TitleRepository):
        count = 0
        for title in titles.get_titles():
            _title = self._titles.get_title(title.title)
            if (_title is title):
                continue
            self._titles.set_title(title.title, title)
            count += 1
        return count


class FileEditor(Editor):
    def __init__(self, path: Path,
                 titles: TitleRepository,
                 drafts: DraftRepository,
                 articles: ArticleRepository) -> None:
        super().__init__(titles, drafts, articles)
        self._path = path

    @staticmethod
    def init(path: Path):
        _path = path.joinpath('.sigili')
        _path.mkdir()
        FileSystemArticleRepository.init(_path)
        FileSystemTitleRepository.init(_path)
        FileSystemDraftRepository.init(_path)

    @classmethod
    def fromPath(cls, path: Path):
        _path = path.joinpath('.sigili')
        titles = FileSystemTitleRepository(_path.joinpath('titles'))
        drafts = FileSystemDraftRepository(_path.joinpath('drafts'))
        a_paths = FileSystemArticleRepository.get_paths(_path)
        articles = FileSystemArticleRepository(a_paths)
        return cls(path, titles, drafts, articles)

    def iterfiles(self):
        # Path.rglob doesn't handle avoiding hidden folders well.
        #
        # Using the more correct root_dir=self.path breaks for a
        # reason I don't care to research at the moment.
        glob = map(Path, iglob(f'{self._path}/**', recursive=True))
        return (_glob.resolve() for _glob in glob if _glob.is_file())

    def load_drafts(self):
        for file in self.iterfiles():
            groups = [Label(part)
                      for part in file.relative_to(self._path).parts]
            title = Label(file.name)
            editOf = self._titles.get_title(title)
            _draft = Draft(
                title,
                file.read_bytes(),
                groups,
                editOf
            )
            self._drafts.set_draft(_draft)
