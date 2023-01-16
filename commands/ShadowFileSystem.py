import sqlite3
import os


class ShadowFileSystem:

    db = sqlite3.connect('./sigil/shadow_fs.db')

    def loadFiles(self, files):
        # Files should include pathname and content
        self.db.execute("""
        --sql
        DROP TABLE IF EXISTS file_info
        --endsql
        """)

        self.db.execute("""
        --sql
        /**
        * refid - populated during hydration, reminder for whatever
        * inode - populated during hydration, used for publishing
        * ctimeMs - populated during hydration, used for publishing
        */
        CREATE TABLE IF NOT EXISTS file_info(
          refid NOT NULL PRIMARY KEY,
          inode NOT NULL UNIQUE,
          ctimeMs NOT NULL,
        ) WITHOUT ROWID
        --endsql
        """)

        for file in files:
            refid_file = open('./sigil/refs/'+file.refid).read()
            open(file.pathname).write(refid_file)
            nf_stat = os.stat(file.pathname)
            self.db.execute("INSERT INTO file_info VALUES(?,?,?)",
                            (file.refid, nf_stat.st_ino, nf_stat.st_ctime))

    def doesInodeExist(self, ino):
        _inoExistsCursor = self.db.execute("""
        --sql
        SELECT COUNT(inode) FROM shadow_filesystem WHERE inode=? LIMIT 1
        --endsql
        """, (ino))
        _inodeCount = _inoExistsCursor.fetchone()[0]
        return _inodeCount > 0
