import detools
import sqlite3
import hashlib
import io
from sigil.repo import RefLog
from sigil.repo.backports.file_digest import file_digest


class Repo:

    def __init__(self):
        self.db = sqlite3.connect("file:.sigil/sigil.db", uri=True)
        self.db.row_factory = sqlite3.Row

    def getArticles(self):
        # you can iterate over a cursor
        return self.db.execute('SELECT * FROM articles')

    def viewRefid(self, refid):
        with RefLog.getVersion(self.db, refid) as _version:
            return _version.read()

    def getHistory(self, refid):
        return RefLog.getHistory(self.db, refid)

    def _createPatch(self, ffrom, fto, fpatch):
        detools.create_patch(ffrom=ffrom, fto=fto,
                             fpatch=fpatch,
                             compression='zstd',
                             use_mmap=False,
                             match_score=0,
                             patch_type='hdiffpatch',
                             algorithm='hdiffpatch')

    def _addNewArticleRef(self, refid, pathname):
        with io.BytesIO(b'') as ffrom, open(pathname, 'rb') as fto, open('.sigil/refs/'+refid, 'wb') as fpatch:
            self._createPatch(ffrom, fto, fpatch)

    def _addArticleRef(self, prefid, crefid, pathname):
        with RefLog.getVersion(self.db, prefid) as ffrom, open(pathname, 'rb') as fto, open('./.sigil/refs/'+crefid, 'wb') as fpatch:
            self._createPatch(ffrom, fto, fpatch)

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
        refid = b''.join([
            bytes.fromhex(prefid),
            bytes.fromhex(pathid),
            bytes.fromhex(contentid)
        ])
        _hash.update(refid)
        return _hash.hexdigest()

    def _updateArticle(self, prefid, crefid, pathname):
        self.db.execute("""
        --sql
        UPDATE articles SET (refid, pathname) = (:crefid, :pathname) WHERE refid = :prefid;
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
