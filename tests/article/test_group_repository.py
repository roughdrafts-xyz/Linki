from contextlib import contextmanager
from pathlib import Path
import pytest
from tempfile import TemporaryDirectory
from sigili.article.group.repository import MemoryGroupRepository, BadGroupRepository, FileSystemGroupRepository


@contextmanager
def getGroupRepository(style: str):
    match style:
        case MemoryGroupRepository.__name__:
            yield MemoryGroupRepository()
        case BadGroupRepository.__name__:
            yield BadGroupRepository()
        case FileSystemGroupRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            _groupPath = FileSystemGroupRepository.initialize_directory(
                _dirPath)
            try:
                yield FileSystemGroupRepository(path=_groupPath)
            finally:
                _dir.cleanup()


styles = {
    MemoryGroupRepository.__name__,
    # BadGroupRepository.__name__,
    FileSystemGroupRepository.__name__,
}


@pytest.mark.parametrize('style', styles)
def test_does_get_groups(style):
    with getGroupRepository(style) as repo:
        expected = 'group'

        repo.add_to_group('0', expected)

        actual = repo.get_groups('0')

        assert sorted([expected]) == sorted(actual)
        # GroupRepository
        #   add_group(refId, group)
        #   get_groups(refId)

        # a refId is part of a group named after its filename
        # any parent folders of that filename become parent groups of that group
        # /hello/world/text.md becomes
        # group(text.md) is a member of group(world) is a member of group(hello)


@pytest.mark.parametrize('style', styles)
def test_does_get_members(style):
    with getGroupRepository(style) as repo:
        expected = '0'

        repo.add_to_group(expected, 'group')

        actual = repo.get_members('group')

        assert sorted([expected]) == sorted(actual)


@pytest.mark.parametrize('style', styles)
def test_does_group_groups(style):
    with getGroupRepository(style) as repo:
        repo.add_to_group('0', 'a')
        repo.add_to_group('a', 'b')

        actual = repo.get_groups('a')

        assert sorted(['b']) == sorted(actual)
