
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import List
from unittest import TestCase

from hypothesis import assume, given
from linki.article import Article, ArticleCollection
from linki.connection import MemoryConnection
from linki.draft import Draft

from linki.editor import FileEditor
from linki.repository import Repository
from linki.testing.strategies.article import an_article
from linki.id import PathLabel
from linki.testing.strategies.draft import a_draft, a_new_draft, some_drafts, some_new_drafts
from linki.title import Title, TitleCollection

test = TestCase()


def do_load_drafts(editor: FileEditor, drafts: List[Draft]):
    for file in editor.repo.path.iterdir():
        if (file.is_file()):
            file.unlink()
        if (file.is_dir() and file.name != '.linki'):
            shutil.rmtree(file)

    for draft in drafts:
        assume(draft.should_update())
        p = editor.repo.path.joinpath(*draft.label.parents)
        p.mkdir(exist_ok=True, parents=True)
        p.joinpath(draft.label.name).write_text(draft.content)
        if (draft.editOf is not None):
            artColl = ArticleCollection(MemoryConnection[Article]())
            titColl = TitleCollection(MemoryConnection[Title]())

            article = draft.editOf
            titColl.set_title(article)
            editor.copy_titles(titColl)

            while (article is not None):
                artColl.merge_article(article)
                article = article.editOf
            editor.copy_articles(artColl)

    editor.load_drafts()


def do_load_draft(editor: FileEditor, draft: Draft):
    do_load_drafts(editor, [draft])
    return editor.repo.path.joinpath(*draft.label.path)


@contextmanager
def get_file_editor():
    with TemporaryDirectory() as _dir:
        path = Path(_dir).resolve().as_uri()
        Repository.create(path)
        yield FileEditor.fromPath(_dir)


@given(a_draft())
def test_loads_drafts(draft: Draft):
    with get_file_editor() as editor:
        path = do_load_draft(editor, draft)
        trunc_path = PathLabel(path.relative_to(editor.repo.path))
        p_draft = editor.repo.drafts.get_draft(trunc_path)
        print(p_draft)
        assert draft == p_draft


@given(a_draft())
def test_does_copy(update: Draft):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        do_load_draft(r_editor, update)

        assert l_editor.copy_articles(r_editor.repo.articles) > 0
        assert l_editor.copy_titles(r_editor.repo.titles) > 0

        test.assertCountEqual(r_editor.repo.articles.get_articles(),
                              l_editor.repo.articles.get_articles())
        test.assertCountEqual(r_editor.repo.titles.get_titles(),
                              l_editor.repo.titles.get_titles())


@given(a_draft())
def test_does_unload_titles(update: Draft):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        do_load_draft(r_editor, update)

        l_editor.copy_articles(r_editor.repo.articles)
        l_editor.copy_titles(r_editor.repo.titles)

        l_editor.unload_titles()
        test.assertCountEqual(
            [file.name for file in r_editor.iterfiles()],
            [file.name for file in l_editor.iterfiles()]
        )


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
        assert draft.label in [
            title.label for title in editor.repo.titles.get_titles()]


@given(a_draft())
def test_does_publish_draft(draft: Draft):
    with get_file_editor() as editor:
        assume(draft.should_update())
        do_load_draft(editor, draft)
        assert editor.publish_drafts() == 1
        assert draft.label in [
            title.label for title in editor.repo.titles.get_titles()]


@given(a_draft())
def test_does_publish_changed_draft_path(draft: Draft):
    with get_file_editor() as editor:
        draft.label.path = ['initial'] + draft.label.path
        init = draft.label
        do_load_draft(editor, draft)
        assert editor.publish_drafts() == 1
        test.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [init]
        )

        draft.label.path[0] = 'changed'
        changed = draft.label
        do_load_draft(editor, draft)
        assert editor.publish_drafts() == 1
        test.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [init, changed]
        )


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    with get_file_editor() as editor:
        do_load_drafts(editor, some_drafts)
        assert 0 < editor.publish_drafts() <= 2
        titles = [title.label for title in editor.repo.titles.get_titles()]
        for draft in some_drafts:
            assert draft.label in titles


@given(some_drafts(2))
def test_does_publish_some_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    with get_file_editor() as editor:
        do_load_drafts(editor, some_drafts)
        assert 0 < editor.publish_drafts() <= 2
        titles = [title.label for title in editor.repo.titles.get_titles()]
        for draft in some_drafts:
            assert draft.label in titles
