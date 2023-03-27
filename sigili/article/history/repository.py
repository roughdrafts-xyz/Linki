from abc import ABC, abstractmethod
import os
from pathlib import Path


class HistoryRepository(ABC):
    @abstractmethod
    def add_edit(self, parentId: str, childId: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_parent(self, childId: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_children(self, parentId: str) -> list[str]:
        raise NotImplementedError


class MemoryHistoryRepository(HistoryRepository):
    def __init__(self) -> None:
        self._parentOf = dict()
        self._childrenOf = dict()

    def add_edit(self, parentId: str, childId: str) -> None:
        self._parentOf[childId] = parentId
        if (parentId not in self._childrenOf):
            self._childrenOf[parentId] = []
        self._childrenOf[parentId].append(childId)

    def get_parent(self, childId: str) -> str:
        return self._parentOf[childId]

    def get_children(self, parentId: str) -> list[str]:
        return self._childrenOf[parentId]


class FileSystemHistoryRepository(HistoryRepository):
    def __init__(self, path: Path):
        self._history = path
        self._parentOf = self._history.joinpath('parentOf')
        self._childrenOf = self._history.joinpath('childrenOf')
        if (not self._history.exists()):
            raise FileNotFoundError(
                f'History folder not found in repository. The folder might not be initialized.')

    @staticmethod
    def initialize_directory(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        _historyPath = path.joinpath('history')
        _historyPath.mkdir()
        _historyPath.joinpath('childrenOf').mkdir()
        _historyPath.joinpath('parentOf').mkdir()
        return _historyPath.resolve()

    def add_edit(self, parentId: str, childId: str) -> None:
        self._parentOf.joinpath(childId).write_text(parentId)

        _childrenPath = self._childrenOf.joinpath(parentId)
        if (not _childrenPath.exists()):
            _childrenPath.mkdir()
        _childrenPath.joinpath(childId).touch()

    def get_parent(self, childId: str) -> str:
        return self._parentOf.joinpath(childId).read_text()

    def get_children(self, parentId: str) -> list[str]:
        return os.listdir(self._childrenOf.joinpath(parentId))
