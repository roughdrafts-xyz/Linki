
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import List
from unittest import TestCase

from hypothesis import assume, given
from linki.article import Article
from linki.draft import Draft

from linki.editor import FileEditor
from linki.repository import Repository
from linki.testing.strategies.article import an_article
from linki.id import PathLabel
from linki.testing.strategies.draft import a_draft, some_drafts, some_new_drafts


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


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    with get_file_editor() as editor:
        repo = editor.repo

        for draft in some_drafts:
            repo.drafts.set_draft(draft)

        draft_count = [draft.label for draft in repo.drafts.get_drafts()]
        update_count = [draft.label for draft in editor.get_updates()]

        editor.publish_drafts()

        title_count = [title.label for title in repo.titles.get_titles()]

        test = TestCase()
        test.assertCountEqual(title_count, draft_count)
        test.assertCountEqual(title_count, update_count)
        test.assertCountEqual(draft_count, update_count)


@given(some_drafts(2))
def test_does_publish_some_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    with get_file_editor() as editor:
        repo = editor.repo

        for draft in some_drafts:
            repo.drafts.set_draft(draft)

        update_count = [draft.label for draft in editor.get_updates()]

        editor.publish_drafts()

        title_count = [title.label for title in repo.titles.get_titles()]

        test = TestCase()
        test.assertCountEqual(title_count, update_count)


@given(an_article(), a_draft())
def test_does_publish_changed_drafts(article: Article, draft: Draft):
    with get_file_editor() as editor:
        repo = editor.repo

        repo.articles.merge_article(article)
        repo.titles.set_title(article)
        draft.editOf = article
        repo.drafts.set_draft(draft)

        assume(draft.should_update())
        assert editor.publish_drafts() == 1


def do_load_draft(editor: FileEditor, draft: Draft):
    for file in editor.repo.path.iterdir():
        if (file.is_file()):
            file.unlink()
        if (file.is_dir() and file.name != '.linki'):
            shutil.rmtree(file)

    p = editor.repo.path.joinpath(*draft.label.parents)
    p.mkdir(exist_ok=True, parents=True)
    p.joinpath(draft.label.name).write_text(draft.content)

    editor.load_drafts()


@given(a_draft())
def test_does_publish_draft(draft: Draft):
    with get_file_editor() as editor:
        assume(draft.should_update())
        do_load_draft(editor, draft)
        assert editor.publish_drafts() == 1


@given(a_draft())
def test_does_publish_changed_draft_path(draft: Draft):
    with get_file_editor() as editor:
        draft.label.path = ['initial'] + draft.label.path
        assume(draft.should_update())
        do_load_draft(editor, draft)
        assert editor.publish_drafts() == 1

        draft.label.path[0] = 'changed'
        assume(draft.should_update())
        do_load_draft(editor, draft)
        assert editor.publish_drafts() == 1
