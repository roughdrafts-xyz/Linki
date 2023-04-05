from abc import ABC, abstractmethod
import os
from pathlib import Path

from sigili.type.id import Label


class GroupRepository(ABC):

    @abstractmethod
    def add_to_group(self, memberId: str, groupId: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_groups_of(self, memberId: str) -> list[Label]:
        raise NotImplementedError

    @abstractmethod
    def get_members_of(self, groupId: str) -> list[Label]:
        raise NotImplementedError

    @abstractmethod
    def get_groups(self) -> dict[Label, list[Label]]:
        return NotImplementedError


class MemoryGroupRepository(GroupRepository):
    def __init__(self) -> None:
        self._byGroup: dict[Label, set[Label]] = dict()
        self._byMember: dict[Label, set[Label]] = dict()

    def add_to_group(self, memberId: str, groupId: str) -> None:
        try:
            _memberId = Label(memberId)
            _groupId = Label(groupId)
        except AttributeError:
            return None

        if (_groupId not in self._byGroup):
            self._byGroup[_groupId] = set()
        if (_memberId not in self._byMember):
            self._byMember[_memberId] = set()
        self._byGroup[_groupId].add(_memberId)
        self._byMember[_memberId].add(_groupId)

    def get_groups_of(self, memberId: str) -> list[Label]:
        return list(self._byMember.get(Label(memberId), []))

    def get_members_of(self, groupId: str) -> list[Label]:
        return list(self._byGroup.get(Label(groupId), []))

    def get_groups(self) -> dict[Label, list[Label]]:
        _byMember: dict[Label, list[Label]] = {}
        for key, value in self._byMember.items():
            _byMember[key] = list(value)
        return _byMember


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
        try:
            _memberId = Label(memberId)
            _groupId = Label(groupId)
        except AttributeError:
            return None

        _memberPath = self._byMember.joinpath(_memberId.name)
        _groupPath = self._byGroup.joinpath(_groupId.name)

        if (_memberPath.exists() and _groupPath.exists()):
            return None

        if (not _memberPath.exists()):
            _memberPath.mkdir()

        if (not _groupPath.exists()):
            _groupPath.mkdir()

        _memberPath.joinpath(groupId).symlink_to(_groupPath)
        _groupPath.joinpath(memberId).symlink_to(_memberPath)

    def get_groups_of(self, memberId: str) -> list[Label]:
        _memberId = Label(memberId)
        _path = self._byMember.joinpath(_memberId.name)
        if (not _path.exists()):
            return []
        return [Label(x) for x in os.listdir(_path)]

    def get_members_of(self, groupId: str) -> list[Label]:
        _groupId = Label(groupId)
        _path = self._byGroup.joinpath(_groupId.name)
        if (not _path.exists()):
            return []
        return [Label(x) for x in os.listdir(_path)]

    def get_groups(self) -> dict[Label, list[Label]]:
        groups: dict[Label, list[Label]] = dict()
        for member in self._byMember.iterdir():
            groups[Label(member.name)] = [
                Label(_member.name) for _member in member.iterdir()]

        return groups
