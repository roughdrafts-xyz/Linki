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
            "file:./.sigil/sigil.db?vfs=zstd", uri=True)
    except sqlite3.OperationalError:
        print("sigil database note found, please run `sigil init`")
        exit(0)

    def addNewArticle(self, refid, pathname, content):
        self.db.execute("""
        --sql
        INSERT INTO articles VALUES(:refid, :pathname, :content)
        --endsql
        """, (refid, pathname, content))

    def updateExistingArticle(self, refid, pathname, content):
        self.db.execute("""
        --sql
        UPDATE articles SET (refid, pathname, content) = (:crefid, :pathname, :content) WHERE refid = :prefid
        --endsql
        """, {'prefid': refid, 'pathname': pathname, 'crefid': 'crefid', 'content': content})
