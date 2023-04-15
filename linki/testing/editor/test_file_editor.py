
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from hypothesis import given
from linki.article import Article

from linki.editor import FileEditor
from linki.repository import Repository
from linki.testing.strategies.article import an_article
from linki.id import Label


@contextmanager
def get_file_editor():
    with TemporaryDirectory() as _dir:
        path = Path(_dir).resolve().as_uri()
        Repository.create(path)
        yield FileEditor.fromPath(_dir)


def test_loads_drafts():
    with get_file_editor() as editor:
        editor._path.joinpath('hello_world.md').write_text('Hello World')
        editor.load_drafts()
        assert editor._drafts.get_draft(Label('hello_world.md')) is not None


@given(an_article())
def test_does_copy(update: Article):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        article = r_editor._articles.merge_article(update)
        r_editor._titles.set_title(article)

        l_editor.copy_articles(r_editor._articles)
        test = TestCase()

        test.assertCountEqual(r_editor._articles.get_articles(),
                              l_editor._articles.get_articles())

        l_editor.copy_titles(r_editor._titles)

        test.assertCountEqual(r_editor._titles.get_titles(),
                              l_editor._titles.get_titles())


@given(an_article())
def test_does_unload_titles(update: Article):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        article = r_editor._articles.merge_article(update)
        r_editor._titles.set_title(article)

        l_editor.copy_articles(r_editor._articles)
        l_editor.copy_titles(r_editor._titles)

        l_editor.unload_titles()
        test = TestCase()
        test.assertCountEqual(
            [title.label.name for title in l_editor._titles.get_titles()],
            [file.name for file in l_editor.iterfiles()]
        )
