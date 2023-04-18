from dataclasses import dataclass
from hashlib import sha224
from pathlib import Path
import re
from typing import List

SHA224 = re.compile(r'[a-f0-9]{56}')


class InvalidIDError(Exception):
    pass


class ID(str):
    def __new__(cls, content):
        if (not cls.isValidID(content)):
            raise InvalidIDError(
                f'{content} is not a Valid ID.\nValid IDs are SSH224 Hashes. Please use the id generator attached to the ID Class you are trying to use.')
        return super().__new__(cls, content)

    @staticmethod
    def isValidID(id: str) -> bool:
        return bool(SHA224.fullmatch(id))


class ArticleID(ID):
    @classmethod
    def getArticleID(cls, label, content, editOf) -> 'ArticleID':
        if (editOf is None):
            _editOf = b''
        else:
            _editOf = str.encode(editOf.articleId)
        _label = str.encode(label.name)
        _content = str.encode(content)
        return cls(sha224(
            b''.join([
                _label,
                _content,
                _editOf,
            ])
        ).hexdigest())


class LabelID(ID):
    @classmethod
    def getLabelID(cls, name: str) -> 'LabelID':
        return cls(sha224(str.encode(name)).hexdigest())


@dataclass
class Label():
    name: str
    path: List[str]
    labelId: LabelID

    def __init__(self, name: str, path: List[str]) -> None:
        if (not self.is_valid(name)):
            raise AttributeError
        self._label = name
        self.name = self.as_safe_string(name)
        self.path = path
        self.labelId = LabelID.getLabelID(self.name)

    @classmethod
    def is_valid(cls, string: str) -> bool:
        if type(string) is not str:
            return False

        if not string:
            return False
        safe_str = cls.as_safe_string(string)
        return (
            (len(string) > 0) and
            (len(safe_str) > 0)
        )

    @ property
    def unsafe_raw_name(self):
        return self._label

    @ staticmethod
    def as_safe_string(string: str) -> str:
        _str = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", string)
        _str = _str.strip()
        _str = _str.strip('.')
        if (not _str):
            _str = "-"
        return _str

    def __repr__(self) -> str:
        return f"Label({self.unsafe_raw_name})"

    def __hash__(self) -> int:
        return hash(self.labelId)


@dataclass
class SimpleLabel(Label):
    name: str
    path: List[str]
    labelId: LabelID

    def __init__(self, name: str) -> None:
        super().__init__(name, [])


@dataclass
class PathLabel(Label):
    def __init__(self, path: Path) -> None:
        super().__init__(path.name)
