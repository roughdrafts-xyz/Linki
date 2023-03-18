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
            self._data = self._path.joinpath('data')
            self._log = self._path.joinpath('log')
            path_is_empty = not any(self._path.iterdir())
            if (
                not self._data.exists() or
                not self._log.exists()
            ) and (path_is_empty):
                self._data.mkdir()
                self._log.mkdir()
            else:
                raise FileExistsError
        else:
            raise FileNotFoundError

    def add_article(self, content: bytes) -> str:
        refDetails = updateRefDetail(refId='0', content=content)
        self._data.joinpath(refDetails.refId).write_bytes(content)
        self._log.joinpath(refDetails.refId).write_text(refDetails.prefId)
        return refDetails.refId

    def get_article(self, refId: str) -> bytes:
        return self._data.joinpath(refId).read_bytes()

    def update_article(self, refId: str, content: bytes) -> str:
        refDetails = updateRefDetail(refId=refId, content=content)
        self._data.joinpath(refDetails.refId).write_bytes(content)
        self._log.joinpath(refDetails.refId).write_text(refDetails.prefId)
        return refDetails.refId

    def get_details(self, refId: str) -> RefDetail:
        prefId = self._log.joinpath(refId).read_text()
        return RefDetail(
            refId=refId,
            prefId=prefId
        )

    def get_refs(self) -> set[str]:
        return set(os.listdir(self._data))
