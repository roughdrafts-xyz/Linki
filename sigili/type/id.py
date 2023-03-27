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
    pass


BlankArticleID = ArticleID(sha224(b'BlankArticleID').hexdigest())


class ContentID(_ID):
    @classmethod
    def getContentID(cls, content: bytes) -> 'ContentID':
        return cls(sha224(content).hexdigest())
    pass


class Title(str):
    @classmethod
    def from_string(cls, title: str) -> 'Title':
        badCharacters = r'\/:*?"<>|'
        badCharacters += r"'"

        _title = str(title)
        _title = _title.strip()
        _title = _title.strip(badCharacters + r".")
        for character in title:
            if ((character in string.whitespace) or
                (character in badCharacters) or
                    (not character.isprintable())):
                _title = _title.replace(character, '_')
        if not _title:
            _title = '_'
        return cls(_title)
