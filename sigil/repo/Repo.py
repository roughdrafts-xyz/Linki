import sqlite3
import shutil
from sys import exit
from sigil.repo._init import init


class Repo:
    def connect(self):
        self.db = sqlite3.connect("file:./.sigil/sigil.db", uri=True)
        self.db.row_factory = sqlite3.Row

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

    def init(self):
        init()
