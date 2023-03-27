from hashlib import sha224
import re

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
    def getArticleID(cls, update: 'ArticleUpdate') -> 'ArticleID':
        _groups = map(str.encode, update.groups)
        _editOf = str.encode(update.editOf or '')
        return cls(sha224(
            b''.join([
                _editOf,
                *_groups,
                update.content
            ])
        ).hexdigest())
    pass


class ContentID(_ID):
    @classmethod
    def getContentID(cls, content: bytes) -> 'ContentID':
        return cls(sha224(content).hexdigest())
    pass


Title = str
