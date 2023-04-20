from collections import Counter
from glob import iglob
from pathlib import Path
from typing import Iterable
from linki.article import ArticleCollection
from linki.draft import Draft
from linki.repository import FileRepository, Repository
from linki.title import Redirect, TitleCollection
from linki.id import PathLabel


class Editor():

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def get_updates(self) -> Iterable[Draft]:
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
                    article = self.merge_title(redirect)
                    changed.append(redirect.label)

        for label in published:
            self.repo.drafts.clear_draft(label)
        for label in changed:
            self.repo.drafts.clear_draft(label)
        return len(published)

    def copy_articles(self, articles: ArticleCollection):
        count = 0
        for article_id in articles.get_articles():
            if (self.repo.articles.has_article(article_id)):
                continue
            article = articles.get_article(article_id)
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
        # Path.rglob doesn't handle avoiding hidden folders well.
        #
        # Using the more correct root_dir=self.path breaks for a
        # reason I don't care to research at the moment.
        return map(Path, iglob(f'{self.repo.path}/**', recursive=True))

    def iterfiles(self):
        glob = self.iterdir()
        return (_glob.resolve() for _glob in glob if _glob.is_file())

    def get_edit_of(self, file: Path):
        content = file.read_text()
        file = file.relative_to(self.repo.path)
        for title in self.repo.titles.get_titles():
            if (
                content == title.content or
                file.parts == title.label.path
            ):
                return title
        return None

    def load_drafts(self):
        for file in self.iterfiles():
            editOf = self.get_edit_of(file)
            label = PathLabel(file.relative_to(self.repo.path))
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
                prev.unlink()
                for crumb in prev.parents:
                    if (crumb == self.repo.path):
                        break
                    crumb.rmdir()
            unload = self.repo.path.joinpath(*title.label.parents)
            unload.mkdir(parents=True, exist_ok=True)
            unload.joinpath(title.label.name).write_text(title.content)


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
