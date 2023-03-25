from abc import ABC, abstractmethod
from hashlib import sha224
import os
from pathlib import Path


class GroupRepository(ABC):

    @abstractmethod
    def add_to_group(self, memberId: str, groupId: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_groups_of(self, memberId: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_members_of(self, groupId: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_groups(self) -> dict[str, list[str]]:
        return NotImplementedError


class MemoryGroupRepository(GroupRepository):
    def __init__(self) -> None:
        self._byGroup: dict[str, list[str]] = dict()
        self._byMember: dict[str, list[str]] = dict()

    def add_to_group(self, memberId: str, groupId: str) -> None:
        _groups = self.get_groups_of(memberId)
        _members = self.get_members_of(groupId)
        if ((memberId in _members) and (groupId in _groups)):
            return None

        if (groupId not in self._byGroup):
            self._byGroup[groupId] = []
        if (memberId not in self._byMember):
            self._byMember[memberId] = []
        self._byGroup[groupId].append(memberId)
        self._byMember[memberId].append(groupId)

    def get_groups_of(self, memberId: str) -> list[str]:
        return self._byMember.get(memberId, [])

    def get_members_of(self, groupId: str) -> list[str]:
        return self._byGroup.get(groupId, [])

    def get_groups(self) -> dict[str, list[str]]:
        return self._byMember


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

        _members = self.get_members_of(groupId)
        _groups = self.get_groups_of(memberId)
        if ((memberId in _members) and (groupId in _groups)):
            return None

        if (not _memberPath.exists()):
            _memberPath.mkdir()

        if (not _groupPath.exists()):
            _groupPath.mkdir()

        _memberPath.joinpath(groupId).symlink_to(_groupPath)
        _groupPath.joinpath(memberId).symlink_to(_memberPath)

    def get_groups_of(self, memberId: str) -> list[str]:
        _path = self._byMember.joinpath(memberId)
        if (not _path.exists()):
            return []
        return os.listdir(_path)

    def get_members_of(self, groupId: str) -> list[str]:
        _path = self._byGroup.joinpath(groupId)
        if (not _path.exists()):
            return []
        return os.listdir(_path)

    def get_groups(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = dict()
        for member in self._byMember.iterdir():
            groups[member.name] = [
                _member.name for _member in member.iterdir()]

        return groups
