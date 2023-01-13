from glob import iglob
import os
from DbActions import DbActions


def _removeOrphans():
    pass


def _updateReflog():
    pass


def _addNewFile(pathname):
    file = open(pathname).read()
    pass


def publish():

    files = iglob('**', recursive=True)

    db = DbActions()

    for file in files:
        if not os.path.isfile(file):
            continue

        _stat = os.stat(file)
        _inodeExists = db.doesInodeExist(_stat.st_ino)
        if not _inodeExists:
            _addNewFile(file)
            continue
