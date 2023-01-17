from glob import iglob
import os
from .DbActions import DbActions


def _removeOrphans():
    pass


def _updateReflog():
    pass


def publish():
    db = DbActions()
    db.connect()

    def _updateExistingFile(pathname):
        db.updateExistingArticle('refid', pathname)

    def _addNewFile(pathname):
        db.addNewArticle('refid', pathname)

    files = iglob('**', recursive=True)
    for file in files:
        if not os.path.isfile(file):
            continue
        _addNewFile(file)
