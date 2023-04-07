from typing import Dict, Iterator, MutableMapping, TypeVar

from sigili.type.id import ID, Label, LabelID

VT = TypeVar('VT')


class Connection(MutableMapping[ID, VT]):
    pass


class MemoryConnection(Connection[ID, VT]):
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
