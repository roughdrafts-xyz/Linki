import sqlite3
from sys import exit


class DbActions:
    def connect(self):
        try:
            self.db = sqlite3.connect("file:./.sigil/sigil.db", uri=True)
        except sqlite3.OperationalError:
            print("sigil database note found, please run `sigil init`")
            exit(0)

    def getArticles(self):
        # you can iterate over a cursor
        return self.db.execute('SELECT * FROM articles')

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
