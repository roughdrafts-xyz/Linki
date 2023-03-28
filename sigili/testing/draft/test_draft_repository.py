from contextlib import contextmanager
from pathlib import Path
from random import choice
from tempfile import TemporaryDirectory
from typing import Iterator, List
from unittest import TestCase

import pytest
from sigili.draft.repository import Draft
from hypothesis import given
from sigili.testing.contexts.draft import getDraftRepository, styles
from sigili.testing.strategies.draft import a_draft, some_drafts


@pytest.mark.parametrize('style', styles)
@given(some_drafts(2))
def test_should_set_a_draft(style, drafts):
    with getDraftRepository(style) as repo:
        for draft in drafts:
            print(draft)
            assert repo.set_draft(draft) == draft


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_get_draft(style, draft):
    with getDraftRepository(style) as repo:
        draft = repo.set_draft(draft)
        assert repo.get_draft(draft.title) == draft


@pytest.mark.parametrize('style', styles)
@given(a_draft())
def test_should_get_drafts(style, draft):
    with getDraftRepository(style) as repo:
        draft = repo.set_draft(draft)
        test = TestCase()
        test.assertCountEqual(repo.get_drafts(), [draft])


@pytest.mark.parametrize('style', styles)
@given(some_drafts(2))
def test_should_get_some_drafts(style, drafts: List[Draft]):
    with getDraftRepository(style) as repo:
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
    with getDraftRepository(style) as repo:
        draft = repo.set_draft(draft)
        assert repo.get_draft(draft.title) == draft

        repo.clear_draft(draft.title)
        assert repo.get_draft(draft.title) == None


@pytest.mark.parametrize('style', styles)
@given(some_drafts(2))
def test_should_clear_some_drafts(style, drafts: Iterator[Draft]):
    with getDraftRepository(style) as repo:
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
