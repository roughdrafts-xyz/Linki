from pathlib import Path
import pickle
from typing import Dict, Iterator, MutableMapping, TypeVar

from linki.id import ID

VT = TypeVar('VT')


class Connection(MutableMapping[ID, VT]):
    pass


class MemoryConnection(Connection[VT]):
    def __init__(self) -> None:
        self.store: Dict[ID, VT] = dict()

    def __setitem__(self, __key: ID, __value: VT) -> None:
        self.store[__key] = __value

    def __getitem__(self, __key: ID) -> VT:
        return self.store[__key]

    def __delitem__(self, __key: ID) -> None:
        del self.store[__key]

    def __iter__(self) -> Iterator[ID]:
        return self.store.__iter__()

    def __len__(self) -> int:
        return self.store.__len__()


class PathConnection(Connection[VT]):
    def __init__(self, path: Path) -> None:
        self.store = path.resolve()
        if (not self.store.is_dir()):
            raise TypeError('Path must be a directory.')

    def __setitem__(self, __key: ID, __value: VT) -> None:
        with self.store.joinpath(__key).open('wb') as item:
            pickle.dump(__value, item)

    def __getitem__(self, __key: ID) -> VT:
        if (not self.__contains__(__key)):
            raise KeyError

        with self.store.joinpath(__key).open('rb') as item:
            return pickle.load(item)

    def __delitem__(self, __key: ID) -> None:
        if (not self.__contains__(__key)):
            raise KeyError
        self.store.joinpath(__key).unlink()

    def __iter__(self) -> Iterator[ID]:
        for item in self.store.iterdir():
            if (item.is_file()):
                yield ID(item.name)

    def __len__(self) -> int:
        return len(list(self.store.iterdir()))

    def __contains__(self, __key: ID) -> bool:
        key_path = self.store.joinpath(__key)
        return key_path.exists() and key_path.is_file()

    @staticmethod
    def create_path(path: str, style: str):
        base = Path(path).resolve()

        if (not base.exists()):
            raise FileNotFoundError
        if (not base.is_dir()):
            raise ValueError

        root = base.joinpath('.linki')
        if (not root.exists()):
            root.mkdir()

        connection = root.joinpath(style)
        connection.mkdir()
        return connection.resolve()

    @staticmethod
    def get_path(path: str, style: str):
        base = Path(path).resolve()

        if (not base.exists()):
            raise FileNotFoundError
        if (not base.is_dir()):
            raise ValueError

        root = base.joinpath('.linki')
        if (not root.exists()):
            raise FileNotFoundError
        if (not root.is_dir()):
            raise ValueError

        connection = root.joinpath(style)
        return connection.resolve()
