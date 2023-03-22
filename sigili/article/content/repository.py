from abc import ABC, abstractmethod
from pathlib import Path
import os
from sigili.article.error import RepositoryMalformedError

from sigili.data.ref import RefDetail, updateRefDetail


class ContentRepository(ABC):

    @abstractmethod
    def add_content(self, content: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_content(self, contentId: str) -> bytes:
        raise NotImplementedError


class MemoryContentRepository(ContentRepository):
    def __init__(self):
        self._data = {}

    def add_content(self, content: bytes) -> str:
        refDetails = updateRefDetail(refId='0', content=content)
        self._data[refDetails.refId] = content
        return refDetails.refId

    def get_content(self, contentId: str) -> bytes:
        return self._data[contentId]


class BadContentRepository(ContentRepository):
    def add_content(self, content: bytes) -> str:
        del content
        return ''

    def get_content(self, contentId: str) -> bytes:
        del contentId
        return b''


class FileSystemContentRepository(ContentRepository):
    def __init__(self, path: Path):
        self._content = path
        if (not self._content.exists()):
            raise FileNotFoundError(
                f'Content folder not found in repository. The folder might not be initialized.')

    @staticmethod
    def initialize_directory(path: Path):
        if (not path.exists()):
            raise FileNotFoundError
        path_is_not_empty = any(path.iterdir())
        if (path_is_not_empty):
            raise FileExistsError
        _contentPath = path.joinpath('content')
        _contentPath.mkdir()
        return _contentPath

    def add_content(self, content: bytes) -> str:
        refDetails = updateRefDetail(refId='0', content=content)
        self._content.joinpath(refDetails.refId).write_bytes(content)
        return refDetails.refId

    def get_content(self, contentId: str) -> bytes:
        return self._content.joinpath(contentId).read_bytes()
