from glob import iglob
from pathlib import Path
from typing import Iterable
from linki.article import ArticleCollection
from linki.draft import Draft
from linki.repository import FileRepository, Repository
from linki.title import TitleCollection
from linki.id import Label


class Editor():

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def get_updates(self) -> Iterable[Draft]:
        for _draft in self.repo.drafts.get_drafts():
            if (_draft.should_update()):
                yield _draft

    def publish_drafts(self) -> int:
        for title in self.repo.titles.get_titles():
            isClear = self.repo.drafts.get_draft(title.label) is None
            if isClear:
                self.repo.titles.clear_title(title.label)

        count = 0
        for draft in self.get_updates():
            count += 1
            article = self.repo.articles.merge_article(draft.asArticle())
            self.repo.titles.set_title(article)
        return count

    def copy_articles(self, articles: ArticleCollection):
        count = 0
        for article_id in articles.get_articles():
            if (self.repo.articles.has_article(article_id)):
                continue
            article = articles.get_article(article_id)
            self.repo.articles.merge_article(article)
            count += 1
        return count

    def copy_titles(self, titles: TitleCollection):
        count = 0
        for title in titles.get_titles():
            _title = self.repo.titles.get_title(title.label)
            if (_title is title):
                continue
            self.repo.titles.set_title(title.article)
            count += 1
        return count


class FileEditor(Editor):
    def __init__(self, repo: FileRepository) -> None:
        super().__init__(repo)
        self.repo = repo

    @classmethod
    def fromPath(cls, base: str | Path):
        path = Path(base).resolve()
        repo = FileRepository(path.as_uri())
        return cls(repo)

    def iterfiles(self):
        # Path.rglob doesn't handle avoiding hidden folders well.
        #
        # Using the more correct root_dir=self.path breaks for a
        # reason I don't care to research at the moment.
        glob = map(Path, iglob(f'{self.repo.path}/**', recursive=True))
        return (_glob.resolve() for _glob in glob if _glob.is_file())

    def load_drafts(self):
        for file in self.iterfiles():
            title = Label(file.name)
            editOf = self.repo.titles.get_title(title)
            _editOf = None
            if (editOf is not None):
                _editOf = editOf.article
            _draft = Draft(
                title,
                file.read_text(),
                _editOf
            )
            self.repo.drafts.set_draft(_draft)

    def unload_titles(self):
        path = Path(self.repo.path)
        for title in self.repo.titles.get_titles():
            path.joinpath(title.label.name).write_text(title.article.content)


class Copier:
    source: Repository
    destination: Editor

    def __init__(self, source: Repository, destination: Editor) -> None:
        self.source = source
        self.destination = destination

    def copy_articles(self):
        return self.destination.copy_articles(self.source.articles)

    def copy_titles(self):
        return self.destination.copy_titles(self.source.titles)


class FileCopier(Copier):
    destination: FileEditor

    def __init__(self, source: Repository, destination: str | Path) -> None:
        self.source = source
        self.destination = FileEditor.fromPath(destination)

    def unload_titles(self):
        self.destination.unload_titles()
