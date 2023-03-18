from dataclasses import dataclass
from hashlib import sha224


@dataclass
class RefDetail():
    refId: str
    prefId: str


def getNewRefId(refId: str, content: bytes) -> str:
    return sha224(b''.join([
        str.encode(refId),
        content
    ])).hexdigest()


def updateRefDetail(refId: str, content: bytes) -> RefDetail:
    return RefDetail(
        prefId=refId,
        refId=getNewRefId(refId=refId, content=content)
    )
