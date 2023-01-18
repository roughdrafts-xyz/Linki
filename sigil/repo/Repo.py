import sqlite3
import shutil
import hashlib
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

    def _generateContentId(self, pathname):
        with open(pathname, 'rb') as file:
            digest = hashlib.file_digest(file, 'sha224')
        return digest.hexdigest()

    def _generatePathnameId(self, pathname):
        _hash = hashlib.sha224()
        _hash.update(str.encode(pathname))
        return _hash.hexdigest()

    def _generateInitialRefid(self, pathname):
        _hash = hashlib.sha224()
        contentid = self._generateContentId(pathname)
        pathid = self._generatePathnameId(pathname)
        _hash.update(str.encode(pathid))
        _hash.update(str.encode(contentid))
        return _hash.hexdigest()

    def _generateNewRefid(self, prefid, pathname):
        _hash = hashlib.sha224()
        contentid = self._generateContentId(pathname)
        pathid = self._generatePathnameId(pathname)
        _hash.update(str.encode(prefid))
        _hash.update(str.encode(pathid))
        _hash.update(str.encode(contentid))
        return _hash.hexdigest()

    def addNewArticle(self, pathname):
        refid = self._generateInitialRefid(pathname)
        self.db.execute("""
        --sql
        INSERT INTO articles VALUES(:refid, :pathname)
        --endsql
        """, [refid, pathname])
        self.db.commit()
        self._addArticleRef(refid, pathname)
        return refid

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
