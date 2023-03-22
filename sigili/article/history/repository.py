from abc import ABC, abstractmethod
import os
from pathlib import Path


class HistoryRepository(ABC):
    @abstractmethod
    def add_edit(self, prefId: str, crefId: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_parent(self, refId: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_children(self, refId: str) -> list[str]:
        raise NotImplementedError


class MemoryHistoryRepository(HistoryRepository):
    def __init__(self) -> None:
        self._parents = dict()
        self._children = dict()

    def add_edit(self, prefId: str, crefId: str) -> None:
        self._parents[crefId] = prefId
        if (prefId not in self._children):
            self._children[prefId] = []
        self._children[prefId].append(crefId)

    def get_parent(self, refId: str) -> str:
        return self._parents[refId]

    def get_children(self, refId: str) -> list[str]:
        return self._children[refId]


class BadHistoryRepository(HistoryRepository):
    def add_edit(self, prefId: str, crefId: str) -> None:
        del prefId
        del crefId
        return None

    def get_parent(self, refId: str) -> str:
        del refId
        return ''

    def get_children(self, refId: str) -> list[str]:
        del refId
        return ['']


class FileSystemHistoryRepository(HistoryRepository):
    def __init__(self, path: Path):
        self._history = path
        self._parents = self._history.joinpath('parents')
        self._children = self._history.joinpath('children')
        if (not self._history.exists()):
            raise FileNotFoundError(
                f'History folder not found in repository. The folder might not be initialized.')

    @staticmethod
    def initialize_directory(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        path_is_not_empty = any(path.iterdir())
        if (path_is_not_empty):
            raise FileExistsError
        path.joinpath('history').mkdir()
        path.joinpath('history', 'children').mkdir()
        path.joinpath('history', 'parents').mkdir()

    def add_edit(self, prefId: str, crefId: str) -> None:
        self._parents.joinpath(crefId).write_text(prefId)

        _refPath = self._children.joinpath(prefId)
        if (not _refPath.exists()):
            _refPath.mkdir()
        _refPath.joinpath(crefId).touch()

    def get_parent(self, refId: str) -> str:
        return self._parents.joinpath(refId).read_text()

    def get_children(self, refId: str) -> list[str]:
        return os.listdir(self._children.joinpath(refId))
