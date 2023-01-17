from glob import iglob
import os
from sigil.repo.Repo import Repo
from sigil.cli.ShadowFileSystem import ShadowFileSystem
import sqlite3


def publish():
    db = Repo()
    sfs = ShadowFileSystem()
    try:
        db.connect()
    except sqlite3.OperationalError:
        print("sigil database not found, please run `sigil init`")
        exit(0)

    try:
        sfs.connect()
    except sqlite3.OperationalError:
        print("Shadow Filesystem not found, please run `sigil init`")
        exit(0)

    def _updateExistingFile(pathname):
        db.updateExistingArticle('refid', pathname)

    def _addNewFile(pathname):
        db.addNewArticle('refid', pathname)

    files = iglob('**', recursive=True)
    for file in files:
        if not os.path.isfile(file):
            continue

        isNewFile = sfs.isNewFile(file)
        if (isNewFile):
            _addNewFile(file)
            continue

        inodeUpdated = sfs.hasInodeUpdated(file)
        if (inodeUpdated):
            _updateExistingFile(file)
            continue
