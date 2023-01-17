from glob import iglob
import os
from sigil.repo.Repo import Repo


def _removeOrphans():
    pass


def _updateReflog():
    pass


def publish():
    db = Repo()
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
