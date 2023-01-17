import sqlite3
import shutil
from sys import exit


class DbActions:
    def connect(self):
        try:
            self.db = sqlite3.connect("file:./.sigil/sigil.db", uri=True)
            self.db.row_factory = sqlite3.Row
        except sqlite3.OperationalError:
            print("sigil database note found, please run `sigil init`")
            exit(0)

    def getArticles(self):
        # you can iterate over a cursor
        return self.db.execute('SELECT * FROM articles')

    def _addArticleRef(self, refid, pathname):
        shutil.copyfile(pathname, './.sigil/refs/'+refid)

    def addNewArticle(self, refid, pathname):
        self.db.execute("""
        --sql
        INSERT INTO articles VALUES(:refid, :pathname)
        --endsql
        """, (refid, pathname))
        self.db.commit()
        self._addArticleRef(refid, pathname)

    def updateExistingArticle(self, refid, pathname):
        self.db.execute("""
        --sql
        UPDATE articles SET (refid, pathname) = (:crefid, :pathname) WHERE refid = :prefid
        --endsql
        """, {'prefid': refid, 'pathname': pathname, 'crefid': 'crefid'})
        self.db.commit()
        self._addArticleRef(refid, pathname)
