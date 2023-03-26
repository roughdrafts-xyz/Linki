from collections import UserString
import re


SHA224 = re.compile(r"[a-f0-9]{56}")


class _ID(UserString):
    def __init__(self, seq: str) -> None:
        assert SHA224.match(seq)
        super().__init__(seq)


class ArticleID(_ID):
    pass


class DraftID(_ID):
    pass


class TitleID(_ID):
    pass


class SourceID(_ID):
    pass
