from abc import ABC, abstractmethod
from hashlib import sha224
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
        self._byGroup = dict()
        self._byMember = dict()

    def add_to_group(self, memberId: str, groupId: str) -> None:
        if (groupId not in self._byGroup):
            self._byGroup[groupId] = []
        if (memberId not in self._byMember):
            self._byMember[memberId] = []
        self._byGroup[groupId].append(memberId)
        self._byMember[memberId].append(groupId)

    def get_groups(self, memberId: str) -> list[str]:
        return self._byMember[memberId]

    def get_members(self, groupId: str) -> list[str]:
        return self._byGroup[groupId]


class FileSystemGroupRepository(GroupRepository):
    def __init__(self, path: Path):
        if (not path.exists()):
            raise FileNotFoundError(
                f'Groups folder not found in repository. The folder might not be initialized.')
        self._byGroup = path.joinpath('byGroup')
        self._byMember = path.joinpath('byMember')

    @staticmethod
    def initialize_directory(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _groupPath = path.joinpath('groups')
        _groupPath.mkdir()
        _groupPath.joinpath('byMember').mkdir()
        _groupPath.joinpath('byGroup').mkdir()
        return _groupPath.resolve()

    def add_to_group(self, memberId: str, groupId: str) -> None:
        _memberPath = self._byMember.joinpath(memberId)
        _groupPath = self._byGroup.joinpath(groupId)

        if (not _memberPath.exists()):
            _memberPath.mkdir()

        if (not _groupPath.exists()):
            _groupPath.mkdir()

        _memberPath.joinpath(groupId).symlink_to(_groupPath)
        _groupPath.joinpath(memberId).symlink_to(_memberPath)

    def get_groups(self, memberId: str) -> list[str]:
        _path = self._byMember.joinpath(memberId)
        return os.listdir(_path)

    def get_members(self, groupId: str) -> list[str]:
        _path = self._byGroup.joinpath(groupId)
        return os.listdir(_path)
