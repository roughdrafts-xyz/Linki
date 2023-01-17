from glob import iglob
import os
from sigil.repo.Repo import Repo
import sqlite3


def _removeOrphans():
    pass


def _updateReflog():
    pass


def publish():
    db = Repo()
    try:
        db.connect()
    except sqlite3.OperationalError:
        print("sigil database note found, please run `sigil init`")
        exit(0)

    def _updateExistingFile(pathname):
        db.updateExistingArticle('refid', pathname)

    def _addNewFile(pathname):
        db.addNewArticle('refid', pathname)

    files = iglob('**', recursive=True)
    for file in files:
        if not os.path.isfile(file):
            continue
        _addNewFile(file)
