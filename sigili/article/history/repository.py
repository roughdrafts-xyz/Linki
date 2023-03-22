from abc import ABC, abstractmethod


class HistoryRepository(ABC):
    @abstractmethod
    def add_edit(self, refId, prefId):
        raise NotImplementedError

    @abstractmethod
    def get_parent(self, refId):
        raise NotImplementedError

    @abstractmethod
    def get_children(self, refId):
        raise NotImplementedError


class MemoryHistoryRepository(HistoryRepository):
    def __init__(self) -> None:
        self._parents = dict()
        self._children = dict()

    def add_edit(self, prefId: str, refId: str) -> None:
        self._parents[refId] = prefId
        if (prefId not in self._children):
            self._children[prefId] = []
        self._children[prefId].append(refId)

    def get_parent(self, refId: str) -> str:
        return self._parents[refId]

    def get_children(self, refId: str) -> list[str]:
        return self._children[refId]
