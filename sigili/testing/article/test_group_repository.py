from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase
import pytest
from tempfile import TemporaryDirectory
from sigili.article.group.repository import MemoryGroupRepository, FileSystemGroupRepository
from sigili.type.id import Label


@contextmanager
def getGroupRepository(style: str, directory: Path | None = None):
    match style:
        case MemoryGroupRepository.__name__:
            yield MemoryGroupRepository()
        case FileSystemGroupRepository.__name__:
            _dir = None
            if (directory is None):
                _dir = TemporaryDirectory()
                _dirPath = Path(_dir.name)
                directory = FileSystemGroupRepository.initialize_directory(
                    _dirPath)
            try:
                yield FileSystemGroupRepository(path=directory)
            finally:
                if (_dir is not None):
                    _dir.cleanup()


styles = {
    MemoryGroupRepository.__name__,
    FileSystemGroupRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
def test_does_get_groups_of(style):
    with getGroupRepository(style) as repo:
        group = 'group'
        expected = Label('group')

        repo.add_to_group('0', group)

        actual = repo.get_groups_of('0')

        test = TestCase()
        test.assertCountEqual([expected], actual)


@pytest.mark.parametrize('style', styles)
def test_does_get_groups(style):
    with getGroupRepository(style) as repo:
        articleId = '0'

        # articles get added to all their groups
        repo.add_to_group(articleId, 'three')
        repo.add_to_group(articleId, 'two')
        repo.add_to_group(articleId, 'one')

        # groups have hierarchies
        repo.add_to_group('three', 'two')
        repo.add_to_group('two', 'one')

        actual = repo.get_groups()

        assert (len(actual)) == 3
        article_groups = actual.get(Label(articleId)) or []
        test = TestCase()
        test.assertCountEqual(
            article_groups, map(Label, ['three', 'two', 'one'])
        )
        test.assertCountEqual(actual.get(Label('three'), []), [Label('two')])
        test.assertCountEqual(actual.get(Label('two'), []), [Label('one')])
        assert actual.get(Label('one')) == None


@pytest.mark.parametrize('style', styles)
def test_does_get_members(style):
    with getGroupRepository(style) as repo:
        expected = '0'

        repo.add_to_group(expected, 'group')

        actual = repo.get_members_of('group')

        test = TestCase()
        test.assertCountEqual([Label(expected)], actual)


@pytest.mark.parametrize('style', styles)
def test_does_group_groups(style):
    with getGroupRepository(style) as repo:
        repo.add_to_group('0', 'a')
        repo.add_to_group('a', 'b')

        actual = repo.get_groups_of('a')

        test = TestCase()
        test.assertCountEqual([Label('b')], actual)


@pytest.mark.parametrize('style', styles)
def test_does_not_add_existing_groups(style):
    with getGroupRepository(style) as repo:
        repo.add_to_group('0', 'a')
        repo.add_to_group('0', 'a')

        actual = repo.get_groups_of('0')

        test = TestCase()
        test.assertCountEqual([Label('a')], actual)
