import sqlite3
import os


class ShadowFileSystem:

    def connect(self):
        self.db = sqlite3.connect('./.sigil/shadow_fs.db')

    def init(self):
        self.connect()
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

    def checkoutArticles(self, articles):
        for article in articles:
            refid_file = open('./sigil/refs/'+article.refid).read()
            open(article.pathname).write(refid_file)
            nfstat = os.stat(article.pathname)
            self.db.execute("INSERT INTO shadow_fstat VALUES(?,?,?,?)",
                            (article.refid, nfstat.st_ino, nfstat.st_mtime_ns, article.pathname))
        self.db.commit()

    def isNewFile(self, file):
        fstat = os.stat(file)
        _inoExistsCursor = self.db.execute("""
        --sql
        SELECT COUNT(inode) FROM shadow_fstat WHERE ino=? LIMIT 1
        --endsql
        """, (fstat.st_ino))
        _inodeCount = _inoExistsCursor.fetchone()[0]
        return _inodeCount < 1

    def hasInodeUpdated(self, file):
        fstat = os.stat(file)
        _inoExistsCursor = self.db.execute("""
        --sql
        SELECT COUNT(inode) FROM shadow_fstat WHERE ino=? AND mtime_ns!=? LIMIT 1
        --endsql
        """, (fstat.st_ino, fstat.st_mtime_ns))
        _inodeCount = _inoExistsCursor.fetchone()[0]
        return _inodeCount > 0
