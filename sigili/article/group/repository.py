from abc import ABC, abstractmethod
import os
from pathlib import Path


class GroupRepository(ABC):

    @abstractmethod
    def add_to_group(self, memberId: str, groupId: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_groups(self, memberId: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_members(self, groupId: str) -> list[str]:
        raise NotImplementedError


class BadGroupRepository(GroupRepository):
    def add_to_group(self, memberId: str, groupId: str) -> None:
        del memberId
        del groupId

    def get_groups(self, memberId: str) -> list[str]:
        del memberId
        return []

    def get_members(self, groupId: str) -> list[str]:
        del groupId
        return []


class MemoryGroupRepository(GroupRepository):
    def __init__(self) -> None:
        self._groups = dict()
        self._members = dict()

    def add_to_group(self, memberId: str, groupId: str) -> None:
        if (groupId not in self._groups):
            self._groups[groupId] = []
        if (memberId not in self._members):
            self._members[memberId] = []
        self._groups[groupId].append(memberId)
        self._members[memberId].append(groupId)

    def get_groups(self, memberId: str) -> list[str]:
        return self._members[memberId]

    def get_members(self, groupId: str) -> list[str]:
        return self._groups[groupId]


class FileSystemGroupRepository(GroupRepository):
    def __init__(self, path: Path):
        if (not path.exists()):
            raise FileNotFoundError(
                f'Groups folder not found in repository. The folder might not be initialized.')
        self._groups = path.joinpath('byGroup')
        self._members = path.joinpath('byMember')

    @staticmethod
    def initialize_directory(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        path_is_not_empty = any(path.iterdir())
        if (path_is_not_empty):
            raise FileExistsError
        _groupPath = path.joinpath('groups')
        _groupPath.mkdir()
        _groupPath.joinpath('byMember').mkdir()
        _groupPath.joinpath('byGroup').mkdir()

    def add_to_group(self, memberId: str, groupId: str) -> None:
        _memberPath = self._members.joinpath(memberId)
        _groupPath = self._groups.joinpath(groupId)

        if (not _memberPath.exists()):
            _memberPath.mkdir()

        if (not _groupPath.exists()):
            _groupPath.mkdir()

        _memberPath.joinpath(groupId).symlink_to(_groupPath)
        _groupPath.joinpath(memberId).symlink_to(_memberPath)

    def get_groups(self, memberId: str) -> list[str]:
        _path = self._members.joinpath(memberId)
        return os.listdir(_path)

    def get_members(self, groupId: str) -> list[str]:
        _path = self._groups.joinpath(groupId)
        return os.listdir(_path)
