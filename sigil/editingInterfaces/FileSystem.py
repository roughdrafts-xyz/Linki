import sqlite3
import os
import shutil
from sigil.repo.RefLog import RefLog
from sigil.repo.Repo import Repo


class FileSystem:
    def __init__(self):
        self.repo = Repo()
        self.db = sqlite3.connect('file:.sigil/shadow_fs.db', uri=True)

    def refreshShadowFs(self):
        # Files should include pathname and content
        self.db.execute("""
        --sql
        DROP TABLE IF EXISTS shadow_fstat
        --endsql
        """)

        self.db.execute("""
        --sql
        /**
        * refid - populated during hydration, reminder for whatever
        * inode - populated during hydration, used for publishing
        * ctimeMs - populated during hydration, used for publishing
        */
        CREATE TABLE IF NOT EXISTS shadow_fstat(
          refid NOT NULL PRIMARY KEY,
          ino NOT NULL UNIQUE,
          mtime_ns NOT NULL,
          pathname NOT NULL
        ) WITHOUT ROWID
        --endsql
        """)
        self.db.commit()

    def _addNewFile(self, refid, file):
        fstat = os.stat(file)
        self.db.execute("INSERT INTO shadow_fstat VALUES(?,?,?,?)",
                        [refid, fstat.st_ino, fstat.st_mtime_ns, file])

    def addNewFile(self, pathname):
        refid = self.repo.addNewArticle(pathname)
        self._addNewFile(refid, pathname)
        self.db.commit()

    def _updateExistingFile(self, crefid, prefid, file):
        fstat = os.stat(file)
        self.db.execute("""
        --sql
        UPDATE shadow_fstat SET (refid, ino, mtime_ns, pathname) = (:crefid, :ino, :mtime_ns, :pathname) WHERE refid=:prefid
        --endsql
        """, [crefid, fstat.st_ino, fstat.st_mtime_ns, file, prefid])

    def updateExistingFile(self, pathname):
        prefid = self.getRefid(pathname)
        crefid = self.repo.updateExistingArticle(prefid, pathname)
        self._updateExistingFile(crefid, prefid, pathname)
        self.db.commit()

    def checkoutArticles(self):
        self.refreshShadowFs()
        articles = self.repo.getArticles()
        for article in articles:
            with RefLog(self.repo.db, article['refid']) as refLog:
                refLog.applyHistory()
                shutil.copyfile(refLog.file.name, article['pathname'])
                self._addNewFile(article['refid'], article['pathname'])
        self.db.commit()

    def isNewFile(self, file):
        fstat = os.stat(file)
        _inoExistsCursor = self.db.execute("""
        --sql
        SELECT COUNT(ino) FROM shadow_fstat WHERE ino=? LIMIT 1
        --endsql
        """, [fstat.st_ino])
        _inodeCount = _inoExistsCursor.fetchone()[0]
        return _inodeCount < 1

    def getRefid(self, file):
        fstat = os.stat(file)
        _refidCursor = self.db.execute("""
        --sql
        SELECT refid FROM shadow_fstat WHERE ino=? LIMIT 1
        --endsql
        """, [fstat.st_ino])
        return _refidCursor.fetchone()[0]

    def hasInodeUpdated(self, file):
        fstat = os.stat(file)
        _inoExistsCursor = self.db.execute("""
        --sql
        SELECT COUNT(ino) FROM shadow_fstat WHERE ino=? AND mtime_ns!=? LIMIT 1
        --endsql
        """, [fstat.st_ino, fstat.st_mtime_ns])
        _inodeCount = _inoExistsCursor.fetchone()[0]
        return _inodeCount > 0
