import detools
import sqlite3
import hashlib
from sigil.repo.backports.file_digest import file_digest
from sigil.repo.RefLog import RefLog
from tempfile import TemporaryFile


class Repo:

    def __init__(self):
        self.db = sqlite3.connect("file:.sigil/sigil.db", uri=True)
        self.db.row_factory = sqlite3.Row

    def getArticles(self):
        # you can iterate over a cursor
        return self.db.execute('SELECT * FROM articles')

    def viewRefid(self, refid):
        with open('.sigil/refs/'+refid, 'rb') as file:
            return file.read()

    def getHistory(self, refid):
        with RefLog(self.db, refid) as refLog:
            return refLog.getHistory()

    def _addNewArticleRef(self, refid, pathname):
        with TemporaryFile('r+b') as refLog, open(pathname, 'rb') as fto, open('.sigil/refs/'+refid, 'wb') as fpatch:
            detools.create_patch(ffrom=refLog, fto=fto, fpatch=fpatch)

    def _addArticleRef(self, prefid, crefid, pathname):
        with RefLog(self.db, prefid) as refLog, open(pathname, 'rb') as fto, open('./.sigil/refs/'+crefid, 'wb') as fpatch:
            refLog.applyHistory()

            detools.create_patch(ffrom=refLog.file, fto=fto,
                                 fpatch=fpatch)

    def _generateContentId(self, pathname):
        with open(pathname, 'rb') as file:
            digest = file_digest(file, hashlib.sha224)
        return digest.hexdigest()

    def _generatePathnameId(self, pathname):
        _hash = hashlib.sha224()
        _hash.update(str.encode(pathname))
        return _hash.hexdigest()

    def _generateNewRefid(self, prefid, pathname):
        _hash = hashlib.sha224()
        contentid = self._generateContentId(pathname)
        pathid = self._generatePathnameId(pathname)
        _hash.update(str.encode(prefid))
        _hash.update(str.encode(pathid))
        _hash.update(str.encode(contentid))
        return _hash.hexdigest()

    def _updateArticle(self, prefid, crefid, pathname):
        self.db.execute("""
        --sql
        UPDATE articles SET (refid, pathname) = (:crefid, :pathname) WHERE refid = :prefid
        --endsql
        """, {'prefid': prefid, 'pathname': pathname, 'crefid': crefid})

    def addNewArticle(self, pathname):
        refid = self._generateNewRefid('', pathname)
        self.db.execute("""
        --sql
        INSERT INTO articles VALUES('0', :pathname);
        """, [pathname])
        self.db.execute("""
        --sql
        UPDATE articles SET (refid, pathname) = (:refid, :pathname) WHERE pathname = :pathname;
        --endsql
        """, {"refid": refid, "pathname": pathname})
        self.db.commit()
        self._addNewArticleRef(refid, pathname)
        return refid

    def updateExistingArticle(self, prefid, pathname):
        crefid = self._generateNewRefid(prefid, pathname)
        self._addArticleRef(prefid, crefid, pathname)
        self._updateArticle(prefid, crefid, pathname)
        self.db.commit()
        return crefid
