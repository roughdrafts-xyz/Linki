import os
import sqlite3
from glob import iglob
from sigil.repo.Repo import Repo
from sigil.cli._ShadowFileSystem import _ShadowFileSystem


def publish():
    db = Repo()
    sfs = _ShadowFileSystem()
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
        prefid = sfs.getRefid(pathname)
        crefid = db.updateExistingArticle(crefid, pathname)
        sfs.updateExistingFile(crefid, prefid, pathname)

    def _addNewFile(pathname):
        refid = db.addNewArticle(pathname)
        sfs.addNewFile(refid, pathname)

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
