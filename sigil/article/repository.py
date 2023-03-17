from abc import ABC, abstractmethod

from sigil.data.ref import RefDetail, updateRefDetail


class ArticleRepository(ABC):

    @abstractmethod
    def add_article(self, content: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_article(self, refId: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def update_article(self, refId: str, content: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_details(self, refId: str) -> RefDetail:
        raise NotImplementedError


class MemoryArticleRepository(ArticleRepository):
    def __init__(self):
        self._log = {}
        self._data = {}

    def add_article(self, content: bytes) -> str:
        refDetails = updateRefDetail(refId='0', content=content)
        self._log[refDetails.refId] = refDetails
        self._data[refDetails.refId] = content
        return refDetails.refId

    def get_article(self, refId: str) -> bytes:
        return self._data[refId]

    def update_article(self, refId: str, content: bytes) -> str:
        refDetails = updateRefDetail(refId=refId, content=content)
        self._log[refDetails.refId] = refDetails
        self._data[refDetails.refId] = content
        return refDetails.refId

    def get_details(self, refId: str) -> RefDetail:
        return self._log[refId]
