from contextlib import contextmanager
from pathlib import Path
from random import choice
from tempfile import TemporaryDirectory
from typing import Iterator, List
from unittest import TestCase

import pytest
from sigili.draft.repository import Draft, FileSystemDraftRepository, MemoryDraftRepository
from hypothesis import given
from sigili.testing.strategies.draft import a_draft, some_drafts


@contextmanager
def getTitleRepository(style: str):
    match style:
        case MemoryDraftRepository.__name__:
            yield MemoryDraftRepository()
        case FileSystemDraftRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _draftPath = FileSystemDraftRepository.initialize_directory(
                _dirPath)
            try:
                yield FileSystemDraftRepository(_draftPath)
            finally:
                _dir.cleanup()


styles = {
    MemoryDraftRepository.__name__,
    FileSystemDraftRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_a_draft(style, draft):
    with getTitleRepository(style) as repo:
        assert repo.set_draft(draft) == draft


@pytest.mark.parametrize('style', styles)
@given(some_drafts(2))
def test_should_a_draft(style, drafts):
    with getTitleRepository(style) as repo:
        for draft in drafts:
            print(draft)
            assert repo.set_draft(draft) == draft


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_get_draft(style, draft):
    with getTitleRepository(style) as repo:
        draft = repo.set_draft(draft)
        assert repo.get_draft(draft.title) == draft


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_get_drafts(style, draft):
    with getTitleRepository(style) as repo:
        draft = repo.set_draft(draft)
        test = TestCase()
        test.assertCountEqual(repo.get_drafts(), [draft])


@pytest.mark.parametrize('style', styles)
@given(some_drafts(2))
def test_should_get_some_drafts(style, drafts: List[Draft]):
    with getTitleRepository(style) as repo:
        _drafts = []
        for draft in drafts:
            repo.set_draft(draft)
            _drafts.append(draft)
        drafts = _drafts
        for draft in repo.get_drafts():
            assert draft in drafts


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_clear_a_draft(style, draft):
    with getTitleRepository(style) as repo:
        draft = repo.set_draft(draft)
        assert repo.get_draft(draft.title) == draft

        repo.clear_draft(draft.title)
        assert repo.get_draft(draft.title) == None


@pytest.mark.parametrize('style', styles)
@given(some_drafts(2))
def test_should_clear_some_drafts(style, drafts: Iterator[Draft]):
    with getTitleRepository(style) as repo:
        _drafts = []
        for draft in drafts:
            draft = repo.set_draft(draft)
            assert repo.get_draft(draft.title) == draft
            _drafts.append(draft)

        cleared_draft = choice(_drafts)
        repo.clear_draft(cleared_draft.title)
        assert repo.get_draft(cleared_draft.title) == None

        for draft in repo.get_drafts():
            assert draft is not cleared_draft
