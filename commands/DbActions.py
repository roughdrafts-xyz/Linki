import sqlite3
import pathlib
from sys import exit


class DbActions:
    try:
        this_path = pathlib.Path(__file__).parent
        zstd_path = this_path.joinpath('../deps/zstd_vfs')
        db = sqlite3.connect(':memory:')
        db.enable_load_extension(True)
        db.load_extension(str(zstd_path))
        db = sqlite3.connect(
            "file:./sigil/sigil.db?mode=ro&vfs=zstd", uri=True)
    except sqlite3.OperationalError:
        print("sigil database note found, please run `sigil init`")
        exit(0)

    def doesInodeExist(self, ino):
        _inoExistsCursor = self.db.execute("""
        --sql
        SELECT COUNT(inode) FROM head WHERE inode=? LIMIT 1
        --endsql
        """, parameters=(ino))
        _inodeCount = _inoExistsCursor.fetchone()[0]
        return _inodeCount > 0

    def addRefLogRow(self, refid, prefid, diff):
        self.db.execute("""
        --sql
        INSERT INTO reflog VALUES(:refid, :prefid, :diff)
        --endsql
        """, parameters=(refid, prefid, diff))
