
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from hypothesis import given
from linki.article import Article

from linki.editor import FileEditor
from linki.repository import Repository
from linki.testing.strategies.article import an_article
from linki.id import PathLabel


@contextmanager
def get_file_editor():
    with TemporaryDirectory() as _dir:
        path = Path(_dir).resolve().as_uri()
        Repository.create(path)
        yield FileEditor.fromPath(_dir)


def test_loads_drafts():
    with get_file_editor() as editor:
        editor_path = Path(editor.repo.path)
        editor_path.joinpath('folder').mkdir()
        path = editor_path.joinpath('folder', 'hello_world.md')
        path.write_text('Hello World')
        editor.load_drafts()
        trunc_path = path.relative_to(editor_path)
        assert editor.repo.drafts.get_draft(
            PathLabel(trunc_path)) is not None


@given(an_article())
def test_does_copy(update: Article):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        article = r_editor.repo.articles.merge_article(update)
        r_editor.repo.titles.set_title(article)

        l_editor.copy_articles(r_editor.repo.articles)
        test = TestCase()

        test.assertCountEqual(r_editor.repo.articles.get_articles(),
                              l_editor.repo.articles.get_articles())

        l_editor.copy_titles(r_editor.repo.titles)

        test.assertCountEqual(r_editor.repo.titles.get_titles(),
                              l_editor.repo.titles.get_titles())


@given(an_article())
def test_does_unload_titles(update: Article):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        article = r_editor.repo.articles.merge_article(update)
        r_editor.repo.titles.set_title(article)

        l_editor.copy_articles(r_editor.repo.articles)
        l_editor.copy_titles(r_editor.repo.titles)

        l_editor.unload_titles()
        test = TestCase()
        test.assertCountEqual(
            [title.label.name for title in l_editor.repo.titles.get_titles()],
            [file.name for file in l_editor.iterfiles()]
        )
