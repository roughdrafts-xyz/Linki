from abc import ABC, abstractmethod
from pathlib import Path
import os

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

    @abstractmethod
    def get_refs(self) -> set[str]:
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

    def get_refs(self) -> set[str]:
        return set(self._data.keys())


class BadArticleRepository(ArticleRepository):
    def add_article(self, content: bytes) -> str:
        del content
        return ''

    def get_article(self, refId: str) -> bytes:
        del refId
        return b''

    def update_article(self, refId: str, content: bytes) -> str:
        del content
        del refId
        return ''

    def get_details(self, refId: str) -> RefDetail:
        del refId
        return RefDetail(
            prefId='',
            refId=''
        )

    def get_refs(self) -> set[str]:
        return {''}


class FileSystemArticleRepository(ArticleRepository):
    def __init__(self, path: Path):
        if (path.exists()):
            self._path = path
        else:
            raise FileNotFoundError

        self._log = {}

    def add_article(self, content: bytes) -> str:
        refDetails = updateRefDetail(refId='0', content=content)
        self._path.joinpath(refDetails.refId).write_bytes(content)
        self._log[refDetails.refId] = refDetails
        return refDetails.refId

    def get_article(self, refId: str) -> bytes:
        return self._path.joinpath(refId).read_bytes()

    def update_article(self, refId: str, content: bytes) -> str:
        refDetails = updateRefDetail(refId=refId, content=content)
        self._path.joinpath(refDetails.refId).write_bytes(content)
        self._log[refDetails.refId] = refDetails
        return refDetails.refId

    def get_details(self, refId: str) -> RefDetail:
        return self._log[refId]

    def get_refs(self) -> set[str]:
        return set(os.listdir(self._path))
