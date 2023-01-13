from glob import iglob
import os
from .DbActions import DbActions


def _removeOrphans():
    pass


def _updateReflog():
    pass


def publish():
    db = DbActions()

    def _updateExistingFile(pathname):
        file = open(pathname).read()
        db.updateExistingArticle('refid', pathname, file)

    def _addNewFile(pathname):
        file = open(pathname).read()
        db.addNewArticle('refid', pathname, file)

    files = iglob('**', recursive=True)
    for file in files:
        if not os.path.isfile(file):
            continue
        _updateExistingFile(file)
