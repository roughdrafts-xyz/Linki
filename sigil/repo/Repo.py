import detools
import sqlite3
import shutil
import hashlib
from sigil.repo._init import init
from sigil.repo.backports.file_digest import file_digest
from sigil.repo.RefLog import RefLog
from tempfile import TemporaryFile


class Repo:

    def connect(self):
        self.db = sqlite3.connect("file:.sigil/sigil.db", uri=True)
        self.db.row_factory = sqlite3.Row

    def getArticles(self):
        # you can iterate over a cursor
        return self.db.execute('SELECT * FROM articles')

    def viewRefid(self, refid):
        with open('.sigil/refs/'+refid, 'rb') as file:
            return file.read()

    def getHistory(self, refid):
        refLog = RefLog(refid, self.db)
        return refLog.getHistory()

    def _addNewArticleRef(self, refid, pathname):
        emptyFile = TemporaryFile('rb')
        fto = open(pathname, 'rb')
        fpatch = open('.sigil/refs/'+refid, 'wb')
        detools.create_patch(ffrom=emptyFile, fto=fto,
                             fpatch=fpatch)

    def _addArticleRef(self, prefid, crefid, pathname):
        ffrom = RefLog(prefid, self.db)
        fto = open(pathname, 'rb')
        fpatch = open('./.sigil/refs/'+crefid, 'wb')

        ffrom.applyHistory()

        detools.create_patch(ffrom=ffrom.file, fto=fto,
                             fpatch=fpatch)

    def _generateContentId(self, pathname):
        with open(pathname, 'rb') as file:
            digest = file_digest(file, hashlib.sha224)
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
        self._addNewArticleRef(refid, pathname)
        self.db.commit()
        return refid

    def updateExistingArticle(self, prefid, pathname):
        crefid = self._generateNewRefid(prefid, pathname)
        self.db.execute("""
        --sql
        UPDATE articles SET (refid, pathname) = (:crefid, :pathname) WHERE refid = :prefid
        --endsql
        """, {'prefid': prefid, 'pathname': pathname, 'crefid': crefid})
        self._addArticleRef(prefid, crefid, pathname)
        self.db.commit()
        return crefid

    def init(self):
        init()
