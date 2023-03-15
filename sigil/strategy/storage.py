from abc import ABC, abstractmethod

from sigil.data.ref import RefDetail, updateRefDetail


class StorageStrategy(ABC):

    @abstractmethod
    def add_bytes(self, update: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_bytes(self, refId: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def update_bytes(self, refId: str, update: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_details(self, refId: str) -> RefDetail:
        raise NotImplementedError


class MemoryStorageStrategy(StorageStrategy):
    def __init__(self):
        self._log = {}
        self._data = {}

    def add_bytes(self, update: bytes) -> str:
        refDetails = updateRefDetail(refId='0', update=update)
        self._log[refDetails.refId] = refDetails
        self._data[refDetails.refId] = update
        return refDetails.refId

    def get_bytes(self, refId: str) -> bytes:
        return self._data[refId]

    def update_bytes(self, refId: str, update: bytes) -> str:
        refDetails = updateRefDetail(refId=refId, update=update)
        self._log[refDetails.refId] = refDetails
        self._data[refDetails.refId] = update
        return refDetails.refId

    def get_details(self, refId: str) -> RefDetail:
        return self._log[refId]
