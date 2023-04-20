from dataclasses import dataclass
from functools import cached_property
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
    def getLabelID(cls, path: List[str]) -> 'LabelID':
        package = b''.join([str.encode(crumb) for crumb in path])
        return cls(sha224(package).hexdigest())


@dataclass
class Label():
    path: List[str]

    def __init__(self, path: List[str]) -> None:
        self.path = [self.as_safe_string(crumb) for crumb in path]
        if not (all(map(self.is_valid, self.path))):
            raise AttributeError

    @cached_property
    def labelId(self):
        return LabelID.getLabelID(self.path)

    @property
    def name(self) -> str:
        return self.path[-1]

    @property
    def parents(self) -> List[str]:
        return self.path[:-1]

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

    @ staticmethod
    def as_safe_string(string: str) -> str:
        _str = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", string)
        _str = _str.strip()
        _str = _str.strip('.')
        if (not _str):
            _str = "-"
        return _str

    def __repr__(self) -> str:
        return f"Label({self.path})"

    def __hash__(self) -> int:
        return hash(self.labelId)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Label):
            return False
        return self.labelId == __value.labelId


class SimpleLabel(Label):
    def __init__(self, name: str) -> None:
        self.unsafe_raw_name = name
        super().__init__([name])


class PathLabel(Label):
    def __init__(self, path: Path) -> None:
        self.path_obj = path
        super().__init__(list(path.parts))
