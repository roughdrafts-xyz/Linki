from dataclasses import dataclass, field
from hashlib import sha224
import re

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
    def getArticleID(cls, update) -> 'ArticleID':
        _groups = [str.encode(group) for group in update.groups]
        if (update.editOf is None):
            _editOf = str.encode(BlankArticleID)
        else:
            _editOf = str.encode(update.editOf)
        return cls(sha224(
            b''.join([
                _editOf,
                *_groups,
                update.content
            ])
        ).hexdigest())


BlankArticleID = ArticleID(sha224(b'BlankArticleID').hexdigest())


class ContentID(ID):
    @classmethod
    def getContentID(cls, content: bytes) -> 'ContentID':
        return cls(sha224(content).hexdigest())


class LabelID(ID):
    @classmethod
    def getLabelID(cls, name: str) -> 'LabelID':
        return cls(sha224(str.encode(name)).hexdigest())


@dataclass
class Label():
    _label: str | None = field(init=False, repr=False, default=None)
    _name: str | None = field(init=False, repr=False, default=None)

    def __init__(self, name: str) -> None:
        if (not self.is_valid(name)):
            raise AttributeError
        self._label = name
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
    def name(self):
        if (self._label is None):
            raise ValueError
        if (self._name is None):
            self._name = self.as_safe_string(self._label)
        return self._name

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
