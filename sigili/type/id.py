import re

SHA224 = re.compile(r'[a-f0-9]{56}')


class InvalidIDError(Exception):
    pass


class _ID(str):
    def __new__(cls, content):
        if (not cls.isValidID(content)):
            raise InvalidIDError()
        return str(content)

    @staticmethod
    def isValidID(id: str) -> bool:
        return bool(SHA224.fullmatch(id))


class ArticleID(_ID):
    pass


class ContentID(_ID):
    pass


class DraftID(_ID):
    pass


class TitleID(_ID):
    pass


class SourceID(_ID):
    pass
