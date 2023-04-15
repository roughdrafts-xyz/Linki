from dataclasses import dataclass
from glob import iglob
from pathlib import Path
from typing import Iterable
from linki.article import ArticleCollection
from linki.draft import Draft, DraftCollection
from linki.repository import Repository
from linki.title import TitleCollection
from linki.id import Label


class Editor():

    def __init__(self, titles: TitleCollection, drafts: DraftCollection, articles: ArticleCollection) -> None:
        self._titles = titles
        self._drafts = drafts
        self._articles = articles

    def get_updates(self) -> Iterable[Draft]:
        for _draft in self._drafts.get_drafts():
            if (_draft.should_update()):
                yield _draft

    def publish_drafts(self) -> int:
        for title in self._titles.get_titles():
            isClear = self._drafts.get_draft(title.label) is None
            if isClear:
                self._titles.clear_title(title.label)

        count = 0
        for draft in self.get_updates():
            count += 1
            article = self._articles.merge_article(draft.asArticle())
            self._titles.set_title(article)
        return count

    def copy_articles(self, articles: ArticleCollection):
        # TODO Make a dataclass of ArticleCollection that simplifies this?

        count = 0
        for article_id in articles.get_articles():
            if (self._articles.has_article(article_id)):
                continue
            article = articles.get_article(article_id)
            self._articles.merge_article(article)
            count += 1
        return count

    def copy_titles(self, titles: TitleCollection):
        count = 0
        for title in titles.get_titles():
            _title = self._titles.get_title(title.label)
            if (_title is title):
                continue
            self._titles.set_title(title.article)
            count += 1
        return count


class FileEditor(Editor):
    def __init__(self, path: Path,
                 titles: TitleCollection,
                 drafts: DraftCollection,
                 articles: ArticleCollection) -> None:
        super().__init__(titles, drafts, articles)
        self._path = path

    @classmethod
    def fromPath(cls, base: str):
        path = Path(base).resolve()
        repo = Repository(path.as_uri())
        return cls(path, repo.titles, repo.drafts, repo.articles)

    def iterfiles(self):
        # Path.rglob doesn't handle avoiding hidden folders well.
        #
        # Using the more correct root_dir=self.path breaks for a
        # reason I don't care to research at the moment.
        glob = map(Path, iglob(f'{self._path}/**', recursive=True))
        return (_glob.resolve() for _glob in glob if _glob.is_file())

    def load_drafts(self):
        for file in self.iterfiles():
            title = Label(file.name)
            editOf = self._titles.get_title(title)
            _editOf = None
            if (editOf is not None):
                _editOf = editOf.article
            _draft = Draft(
                title,
                file.read_bytes(),
                _editOf
            )
            self._drafts.set_draft(_draft)

    def unload_titles(self):
        for title in self._titles.get_titles():
            self._path.joinpath(title.label.name).write_bytes(
                title.article.content)
