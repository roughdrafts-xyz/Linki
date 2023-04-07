from pathlib import Path
import pickle
from typing import Dict, Iterator, MutableMapping, TypeVar

from sigili.type.id import ID

VT = TypeVar('VT')


class Connection(MutableMapping[ID, VT]):
    pass


class MemoryConnection(Connection[VT]):
    def __init__(self) -> None:
        self._: Dict[ID, VT] = dict()

    def __setitem__(self, __key: ID, __value: VT) -> None:
        self._[__key] = __value

    def __getitem__(self, __key: ID) -> VT:
        return self._[__key]

    def __delitem__(self, __key: ID) -> None:
        del self._[__key]

    def __iter__(self) -> Iterator[ID]:
        return self._.__iter__()

    def __len__(self) -> int:
        return self._.__len__()


class PathConnection(Connection[VT]):
    def __init__(self, path: Path) -> None:
        self._ = path.resolve()
        if (not self._.is_dir()):
            raise TypeError('Path must be a directory.')

    def __setitem__(self, __key: ID, __value: VT) -> None:
        with self._.joinpath(__key).open('wb') as _:
            pickle.dump(__value, _)

    def __getitem__(self, __key: ID) -> VT:
        key_path = self._.joinpath(__key)
        if (not key_path.exists()):
            raise KeyError

        with self._.joinpath(__key).open('rb') as _:
            return pickle.load(_)

    def __delitem__(self, __key: ID) -> None:
        key_path = self._.joinpath(__key)
        if (not key_path.exists()):
            raise KeyError
        key_path.unlink()

    def __iter__(self) -> Iterator[ID]:
        for _ in self._.iterdir():
            if (_.is_file()):
                yield ID(_.name)

    def __len__(self) -> int:
        return len(list(self._.iterdir()))
