from itertools import zip_longest
from pathlib import Path
from typing import Iterable

from linki.article import ArticleCollection
from linki.connection import SparseConnection
from linki.draft import BaseArticle, Draft
from linki.repository import FileRepository, Repository
from linki.title import BaseArticle, Redirect, TitleCollection
from linki.id import PathLabel


class Editor():

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def get_updates(self) -> Iterable[BaseArticle]:
        for _draft in self.repo.drafts.get_drafts():
            if (_draft.should_update()):
                yield _draft

    def merge_title(self, draft):
        self.repo.articles.merge_article(draft)
        self.repo.titles.set_title(draft)
        return draft

    def publish_drafts(self) -> int:
        published = []
        changed = []
        for draft in self.get_updates():
            article = self.merge_title(draft)
            published.append(draft.label)
            if (article.editOf is not None):
                if (article.label != article.editOf.label):
                    redirect = Redirect(
                        article.editOf,
                        article.label
                    )
                    self.merge_title(redirect)
                    changed.append(article.label)

        for label in published:
            self.repo.drafts.clear_draft(label)
        for label in changed:
            self.repo.drafts.clear_draft(label)
        return len(published)

    def copy_articles(self, articles: ArticleCollection):
        count = 0
        for article in articles.get_articles():
            if (article is None):
                continue
            self.repo.articles.merge_article(article)
            count += 1
        return count

    def copy_titles(self, titles: TitleCollection):
        count = 0
        for n_title in titles.get_titles():
            o_title = self.repo.titles.get_title(n_title.label)
            if (o_title == n_title):
                continue
            self.repo.titles.set_title(n_title)
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

    def iterdir(self):
        for path in self.repo.path.rglob('*'):
            if ('.linki' not in path.parts and
                        path != self.repo.path
                    ):
                yield path

    def iterfiles(self):
        glob = self.iterdir()
        return (_glob.resolve() for _glob in glob if _glob.is_file())

    def load_drafts(self):
        for file in self.iterfiles():
            shadow = self.repo.shadows.get_shadow(file)
            editOf = None
            if (shadow is not None):
                editOf = shadow.article
            label = PathLabel(file, self.repo.path)
            _draft = Draft(
                label,
                file.read_text(),
                editOf
            )

            self.repo.drafts.set_draft(_draft)

    def unload_titles(self):
        for title in self.repo.titles.get_titles():
            if (title.redirect is not None):
                prev = self.repo.path.joinpath(*title.label.path)
                prev.unlink(missing_ok=True)
                for crumb in prev.parents:
                    if (crumb == self.repo.path):
                        break
                    if (crumb.exists()):
                        crumb.rmdir()
                continue
            unload = self.repo.path.joinpath(*title.label.parents)
            unload.mkdir(parents=True, exist_ok=True)
            unload = unload.joinpath(title.label.name)
            unload.write_text(title.content)
            self.repo.shadows.add_shadow(title, unload.resolve())


class Copier:
    source: Repository
    destination: Editor

    def __init__(self, source: Repository, destination: Editor) -> None:
        self.source = source
        self.destination = destination
        self.articles = self.source.articles
        self.titles = self.source.titles
        if (self.source.connection.url != self.source.connection.root):
            self.articles = ArticleCollection(SparseConnection(
                self.source.articles.store, self.should_copy))
            self.titles = TitleCollection(SparseConnection(
                self.source.titles.store, self.should_copy))

    def should_copy(self, article: BaseArticle) -> bool:
        a = article.label.path
        b = self.source.connection.path
        for (x, y) in zip_longest(a, b):
            if (y is None):
                return True
            if (x != y):
                return False
        return True

    def copy_articles(self):
        return self.destination.copy_articles(self.articles)

    def copy_titles(self):
        return self.destination.copy_titles(self.titles)


class FileCopier(Copier):
    destination: FileEditor

    def __init__(self, source: Repository, destination: str | Path) -> None:
        self.source = source
        self.destination = FileEditor.fromPath(destination)
        super().__init__(self.source, self.destination)

    def unload_titles(self):
        self.destination.unload_titles()
