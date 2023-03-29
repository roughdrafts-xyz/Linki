from dataclasses import dataclass, field
from hashlib import sha224
import re
import string

SHA224 = re.compile(r'[a-f0-9]{56}')


class InvalidIDError(Exception):
    pass


class _ID(str):
    def __new__(cls, content):
        if (not cls.isValidID(content)):
            raise InvalidIDError(
                f'{content} is not a Valid ID.\nValid IDs are SSH224 Hashes. Please use the id generator attached to the ID Class you are trying to use.')
        return super().__new__(cls, content)

    @staticmethod
    def isValidID(id: str) -> bool:
        return bool(SHA224.fullmatch(id))


class ArticleID(_ID):
    @classmethod
    def getArticleID(cls, update) -> 'ArticleID':
        _groups = map(str.encode, update.groups)
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


class ContentID(_ID):
    @classmethod
    def getContentID(cls, content: bytes) -> 'ContentID':
        return cls(sha224(content).hexdigest())


class LabelID(_ID):
    @classmethod
    def getLabelID(cls, name: str) -> 'LabelID':
        return cls(sha224(str.encode(name)).hexdigest())


@dataclass
class Label():
    _label: str | None = field(init=False, repr=False, default=None)
    _name: str | None = field(init=False, repr=False, default=None)

    def __init__(self, name: str) -> None:
        if (not str or len(name) < 1):
            raise AttributeError
        self._label = name
        self.labelId = LabelID.getLabelID(self.name)

    @property
    def name(self):
        if (self._label is None):
            raise ValueError
        if (self._name is None):
            self._name = self.as_safe_string(self._label)
        return self._name

    @property
    def unsafe_raw_name(self):
        return self._label

    @staticmethod
    def as_safe_string(string: str) -> str:
        _str = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", string)
        _str = _str.strip()
        if (not _str):
            _str = "-"
        return _str

    def __hash__(self) -> int:
        return hash(self.labelId)
