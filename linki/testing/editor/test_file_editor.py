
from contextlib import contextmanager
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
from typing import Set
from unittest import TestCase

from hypothesis import HealthCheck, assume, given, settings
import msgspec
from linki.article import Article, BaseArticle
from linki.draft import BaseArticle

from linki.editor import FileEditor
from linki.repository import FileRepository
from linki.testing.strategies.article import an_article
from linki.id import Label, PathLabel, SimpleLabel
from linki.testing.strategies.draft import a_draft, some_drafts, some_new_drafts
from linki.title import BaseArticle


case_tester = TestCase()


def do_load_drafts(editor: FileEditor, drafts: Set[BaseArticle]):
    for file in editor.repo.path.iterdir():
        if (file.is_file()):
            file.unlink()
        if (file.is_dir() and file.name != '.linki'):
            shutil.rmtree(file)

    for draft in drafts:
        if (draft.editOf is not None):
            article = draft.editOf
            p = editor.repo.path.joinpath(*article.label.parents)
            p.mkdir(exist_ok=True, parents=True)
            p = p.joinpath(article.label.name)
            p.write_text(article.content)

            editor.repo.shadows.add_shadow(article, p.resolve())

            c = editor.repo.path.joinpath(*draft.label.parents)
            c.mkdir(exist_ok=True, parents=True)
            c = c.joinpath(draft.label.name)
            p = p.replace(c)
            p.write_text(draft.content)

        else:
            p = editor.repo.path.joinpath(*draft.label.parents)
            p.mkdir(exist_ok=True, parents=True)
            p.joinpath(draft.label.name).write_text(draft.content)

    editor.load_drafts()


def do_load_draft(editor: FileEditor, draft: BaseArticle):
    do_load_drafts(editor, {draft})
    return editor.repo.path.joinpath(*draft.label.path)


@contextmanager
def get_file_editor():
    with TemporaryDirectory() as _dir:
        path = Path(_dir).resolve()
        FileRepository.createPath(path)
        yield FileEditor.fromPath(_dir)


@given(some_drafts(2))
@settings(suppress_health_check=[
    HealthCheck.filter_too_much, HealthCheck.too_slow
])
def test_loads_drafts(drafts: Set[BaseArticle]):
    with get_file_editor() as editor:
        do_load_drafts(editor, drafts)
        loaded_drafts = set(editor.repo.drafts.get_drafts())
        assert len(drafts) == len(loaded_drafts)
        assert drafts == loaded_drafts


@given(some_drafts(2))
@settings(suppress_health_check=[HealthCheck.filter_too_much])
def test_does_copy(updates: Set[BaseArticle]):
    with get_file_editor() as r_editor, get_file_editor() as l_editor:
        do_load_drafts(r_editor, updates)
        r_editor.publish_drafts()

        assume(r_editor.repo.get_count('articles') > 0)
        assume(r_editor.repo.get_count('articles') >=
               r_editor.repo.get_count('titles'))

        l_editor.copy_articles(r_editor.repo.articles)
        l_editor.copy_titles(r_editor.repo.titles)

        case_tester.assertCountEqual(r_editor.repo.articles.get_articles(),
                                     l_editor.repo.articles.get_articles())
        case_tester.assertCountEqual(r_editor.repo.titles.get_titles(),
                                     l_editor.repo.titles.get_titles())


@given(some_drafts(2))
@settings(suppress_health_check=[HealthCheck.filter_too_much])
def test_unload_titles(drafts: Set[BaseArticle]):
    with get_file_editor() as editor:
        do_load_drafts(editor, drafts)
        editor.publish_drafts()
        editor.unload_titles()
        file_labels = [PathLabel(path, editor.repo.path)
                       for path in editor.iterfiles()]
        title_labels = [
            title.label for title in editor.repo.titles.get_titles()]
        for label in file_labels:
            assert label in title_labels


@given(an_article(), a_draft())
def test_does_publish_changed_drafts(article: BaseArticle, draft: BaseArticle):
    with get_file_editor() as editor:
        repo = editor.repo

        repo.articles.merge_article(article)
        repo.titles.set_title(article)
        draft = msgspec.structs.replace(draft, editOf=article)
        repo.drafts.set_draft(draft)

        assume(draft.should_update())
        assert editor.publish_drafts() == 1
        assert draft.label in [
            title.label for title in editor.repo.titles.get_titles()]


@given(a_draft())
def test_does_publish_draft(draft: BaseArticle):
    with get_file_editor() as editor:
        assume(draft.should_update())
        do_load_draft(editor, draft)
        assert editor.publish_drafts() == 1
        assert draft.label in [
            title.label for title in editor.repo.titles.get_titles()]


def test_does_publish_changed_draft_path():
    with get_file_editor() as editor:
        draft = Article(SimpleLabel('hello'), 'hello', None)
        o_draft = msgspec.structs.replace(
            draft, label=Label(['initial', *draft.label.path]))
        n_draft = msgspec.structs.replace(draft, editOf=o_draft, label=Label(
            ['changed', *draft.label.path]))
        z_draft = msgspec.structs.replace(draft, editOf=n_draft, label=Label(
            ['final_z', *draft.label.path]))

        do_load_draft(editor, o_draft)
        assert editor.publish_drafts() == 1
        case_tester.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [o_draft.label]
        )

        do_load_draft(editor, n_draft)
        assert editor.publish_drafts() == 1
        case_tester.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [o_draft.label, n_draft.label]
        )
        g_o_draft = editor.repo.titles.get_title(o_draft.label)
        assert g_o_draft is not None
        assert g_o_draft.redirect == n_draft.label

        do_load_draft(editor, z_draft)
        assert editor.publish_drafts() == 1
        case_tester.assertCountEqual(
            [title.label for title in editor.repo.titles.get_titles()],
            [o_draft.label, n_draft.label, z_draft.label]
        )

        g_n_draft = editor.repo.titles.get_title(n_draft.label)
        assert g_n_draft is not None
        assert g_o_draft.redirect == n_draft.label
        assert g_n_draft.redirect == z_draft.label


@given(some_new_drafts(2))
def test_does_publish_some_new_drafts(some_drafts: Set[BaseArticle]):
    with get_file_editor() as editor:
        do_load_drafts(editor, some_drafts)
        assert 0 < editor.publish_drafts() <= 2
        titles = [title.label for title in editor.repo.titles.get_titles()]
        for draft in some_drafts:
            assert draft.label in titles
