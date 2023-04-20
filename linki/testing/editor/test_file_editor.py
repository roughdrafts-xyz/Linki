
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
from linki.id import Label, PathLabel, SimpleLabel
from linki.testing.strategies.draft import a_draft, a_new_draft, some_drafts, some_new_drafts
from linki.title import Title, TitleCollection

test = TestCase()


def do_load_drafts(editor: FileEditor, drafts: List[Draft], should_update: bool = False):
    for file in editor.repo.path.iterdir():
        if (file.is_file()):
            file.unlink()
        if (file.is_dir() and file.name != '.linki'):
            shutil.rmtree(file)

    for draft in drafts:
        if (should_update):
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
        assert draft == p_draft


@given(some_drafts(2))
def test_does_copy(updates: List[Draft]):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        do_load_drafts(r_editor, updates)
        r_editor.publish_drafts()

        assume(r_editor.repo.get_count('articles') > 0)
        assume(r_editor.repo.get_count('articles') >=
               r_editor.repo.get_count('titles'))

        l_editor.copy_articles(r_editor.repo.articles)
        l_editor.copy_titles(r_editor.repo.titles)

        test.assertCountEqual(r_editor.repo.articles.get_articles(),
                              l_editor.repo.articles.get_articles())
        test.assertCountEqual(r_editor.repo.titles.get_titles(),
                              l_editor.repo.titles.get_titles())


@given(a_draft())
def test_does_unload_titles(update: Draft):
    with get_file_editor() as editor:
        do_load_draft(editor, update)

        editor.unload_titles()
        files = []
        for file in editor.iterfiles():
            parts = file.relative_to(editor.repo.path).parts
            files.append(list(parts))
        test.assertCountEqual(
            files,
            [update.label.path]
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


def test_does_publish_changed_draft_path():
    with get_file_editor() as editor:
        draft = Draft(SimpleLabel('hello'), 'hello')
        o_draft = Draft.fromArticle(draft)
        n_draft = Draft.fromArticle(draft)
        z_draft = Draft.fromArticle(draft)

        o_draft.label = Label(['initial'] + o_draft.label.path)
        n_draft.label = Label(['changed'] + n_draft.label.path)
        z_draft.label = Label(['final_z'] + z_draft.label.path)
        n_draft.editOf = o_draft
        z_draft.editOf = n_draft

        do_load_draft(editor, o_draft)
        assert editor.publish_drafts() == 1
        test.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [o_draft.label]
        )

        do_load_draft(editor, n_draft)
        assert editor.publish_drafts() == 1
        test.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [o_draft.label, n_draft.label]
        )
        g_o_draft = editor.repo.titles.get_title(o_draft.label)
        assert g_o_draft is not None
        assert g_o_draft.redirect == n_draft.label

        do_load_draft(editor, z_draft)
        assert editor.publish_drafts() == 1
        test.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [o_draft.label, n_draft.label, z_draft.label]
        )

        g_n_draft = editor.repo.titles.get_title(n_draft.label)
        assert g_n_draft is not None
        assert g_o_draft.redirect == n_draft.label
        assert g_n_draft.redirect == z_draft.label


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: List[Draft]):
    some_drafts = list(some_drafts)
    with get_file_editor() as editor:
        do_load_drafts(editor, some_drafts)
        assert 0 < editor.publish_drafts() <= 2
        titles = [title.label for title in editor.repo.titles.get_titles()]
        for draft in some_drafts:
            assert draft.label in titles
