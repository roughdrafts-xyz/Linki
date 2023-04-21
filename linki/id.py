from dataclasses import dataclass
from functools import cached_property
from hashlib import sha224
from pathlib import Path
import re
from typing import List

import msgspec

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


class Label(msgspec.Struct, kw_only=True, dict=True):
    path: List[str]

    @classmethod
    def fromUnsafeString(cls, unsafe_raw_name: str):
        label = cls(path=[unsafe_raw_name])
        label.clean_path()
        return label

    @classmethod
    def fromPath(cls, path: Path, root: Path | None = None):
        if root is not None:
            root = root.resolve()
            path = path.relative_to(root)
        label = cls(path=list(path.parts))
        label.clean_path()
        return label

    @cached_property
    def labelId(self):
        return LabelID.getLabelID(self.path)

    @property
    def name(self) -> str:
        return self.path[-1]

    @property
    def parents(self) -> List[str]:
        return self.path[:-1]

    def clean_path(self) -> None:
        self.path = [self.as_safe_string(crumb) for crumb in self.path]
        if not (all(map(self.is_valid, self.path))):
            raise AttributeError

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
        s = str(string).strip().replace(" ", "_")
        s = re.sub(r"(?u)[^-\w.]", "", s)
        if s in {"", ".", ".."}:
            s = '-'
        return s


def SimpleLabel(name: str):
    return Label.fromUnsafeString(name)


def PathLabel(path: Path, root: Path | None = None):
    return Label.fromPath(path, root)
