import copy
from io import BytesIO
from pathlib import Path
import pickle
from typing import Callable, Dict, Iterator, MutableMapping, TypeVar
from urllib.error import HTTPError
from urllib.parse import ParseResult
from urllib.request import urlopen

import msgspec


from linki.id import ID

VT = TypeVar('VT')


class Connection(MutableMapping[ID, VT]):
    def __setitem__(self, __key: ID, __value: VT) -> None:  # type: ignore
        pass

    def __delitem__(self, __key: ID) -> None:  # type: ignore
        pass

    def __getitem__(self, __key: ID) -> VT:  # type: ignore
        pass

    def __iter__(self) -> Iterator[ID]:  # type: ignore
        pass

    def __len__(self) -> int:  # type: ignore
        pass

    def toStream(self) -> bytes:
        items = [self[label] for label in self]
        if (any([not isinstance(item, msgspec.Struct) for item in items])):
            raise AttributeError
        encode = msgspec.msgpack.encode(items)
        return encode

    def toFile(self) -> BytesIO:
        return BytesIO(self.toStream())


class MemoryConnection(Connection[VT]):
    def __init__(self) -> None:
        self.store: Dict[ID, VT] = dict()

    def __setitem__(self, __key: ID, __value: VT) -> None:
        self.store[__key] = copy.deepcopy(__value)

    def __getitem__(self, __key: ID) -> VT:
        return copy.deepcopy(self.store[__key])

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
            raise FileNotFoundError

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


class ROWebConnection(Connection[VT]):
    def __init__(self, url: ParseResult, style: str) -> None:
        if (style not in ['titles', 'articles']):
            raise NotImplementedError
        self.url = f'{url.geturl()}pickles/{style}/'
        self.count_url = f'{url.geturl()}count/{style}/'
        self.style = style

    def __getitem__(self, __key: ID) -> 'Title | Article':  # type: ignore
        try:
            url = f"{self.url}{__key}"
            res = urlopen(url).read()
            return pickle.loads(res)
        except HTTPError:
            raise KeyError

    def __iter__(self) -> Iterator[ID]:
        res = urlopen(self.url).read()
        unpickle = pickle.loads(res)
        for item in unpickle:
            if (self.style == 'articles'):
                yield item.articleId

            if (self.style == 'titles'):
                yield item.label.labelId

    def __len__(self) -> int:
        res = urlopen(self.count_url).read()
        return res


class SparseConnection(Connection[VT]):
    def __init__(self, store: Connection[VT], identifier: Callable[[VT], bool]) -> None:
        super().__init__()
        self.store = store
        self.identifies = identifier

    def __getitem__(self, __key: ID) -> VT:
        return self.store[__key]

    def __iter__(self) -> Iterator[ID]:
        for (key, item) in self.store.items():
            if (self.identifies(item)):
                yield key

    def __len__(self) -> int:
        return self.store.__len__()


class CountError(Exception):
    def __init__(self, options: list[ID], message: str | None = None) -> None:
        self.options = options
        super().__init__(message)
