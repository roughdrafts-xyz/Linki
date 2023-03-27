from abc import ABC, abstractmethod
from hashlib import sha224
from pathlib import Path

from sigili.type.id import ContentID


class ContentRepository(ABC):
    @abstractmethod
    def add_content(self, content: bytes) -> ContentID:
        raise NotImplementedError

    @abstractmethod
    def get_content(self, contentId: str) -> bytes:
        raise NotImplementedError


class MemoryContentRepository(ContentRepository):
    def __init__(self):
        self._data = {}

    def add_content(self, content: bytes) -> ContentID:
        contentId = ContentID.getContentID(content)
        self._data[contentId] = content
        return contentId

    def get_content(self, contentId: str) -> bytes:
        return self._data[contentId]


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
        _contentPath = path.joinpath('content')
        _contentPath.mkdir()
        return _contentPath.resolve()

    def add_content(self, content: bytes) -> ContentID:
        contentId = self.getContentID(content)
        self._content.joinpath(contentId).write_bytes(content)
        return contentId

    def get_content(self, contentId: str) -> bytes:
        return self._content.joinpath(contentId).read_bytes()
