
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List
from unittest import TestCase

from hypothesis import given

from sigili.article.repository import ArticleUpdate, MemoryArticleRepository
from sigili.editor import Editor, FileEditor
from sigili.draft.repository import Draft, MemoryDraftRepository
from sigili.testing.strategies.article import an_article_update
from sigili.testing.strategies.draft import a_draft, a_new_draft, some_drafts, some_new_drafts
from sigili.title.repository import MemoryTitleRepository, Title


@contextmanager
def get_file_editor():
    with TemporaryDirectory() as _dir:
        _path = Path(_dir)
        FileEditor.init(_path)
        yield FileEditor.fromPath(_path)


def test_loads_drafts():
    with get_file_editor() as editor:
        editor._path.joinpath('hello_world.md').write_text('Hello World')
        editor.load_drafts()
