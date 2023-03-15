from dataclasses import dataclass
from hashlib import sha224


@dataclass
class RefDetail():
    refId: str
    prefId: str


def getNewRefId(refId: str, update: bytes) -> str:
    return sha224(b''.join([
        str.encode(refId),
        update
    ])).hexdigest()


def updateRefDetail(refId: str, update: bytes) -> RefDetail:
    return RefDetail(
        prefId=refId,
        refId=getNewRefId(refId=refId, update=update)
    )
