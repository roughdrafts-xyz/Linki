import detools
import sqlite3
import hashlib
import io
import os
from sigil.repo.abc import Repo
from sigil.repo.LocalRepo.init import getRepoPath
from sigil.repo.LocalRepo import RefLog
from sigil.repo.backports.file_digest import file_digest


class LocalRepo(Repo):

    def __init__(self, pathname=None, bare=False):
        self.path = getRepoPath(pathname=pathname, bare=bare)
        dbPath = self.path.joinpath('sigil.db')
        self.db = sqlite3.connect(f"file:{dbPath}", uri=True)
        self.db.row_factory = sqlite3.Row

    # I guess this should always return a set since refs should never be duplicates?
    def getRefIds(self) -> set:
        return set(os.listdir(self.path.joinpath('refs')))

    def getRef(self, ref):
        return self.path.joinpath('refs').read_bytes(ref)

    def getRefs(self, refs: set):
        return map(self.getRef, refs)

    def copy(self, remote: Repo, refs: set):
        refPath = self.path.joinpath('refs')
        for ref in refs:
            remoteRef = remote.getRef(ref)
            # add ref to folder
            refPath.joinpath(ref).write_bytes(remoteRef)
            # add information to database

    def getRemotePath(self):
        return str(self.path.resolve())

    def getRemoteStyle(self):
        # TODO This method might lead to conflicts later.
        return "local"

    # TODO need to do a list comprehension to make this correct to the standard.
    def getRemotes(self) -> list:
        return self.db.execute('SELECT * FROM remotes')

    def addRemote(self, remote):
        pathname = remote.getRemotePath()
        style = remote.getRemoteStyle()
        self.db.execute("""
        --sql
        INSERT INTO remotes VALUES(:pathname, :style);
        """, [pathname, style])
        self.db.commit()

    def delRemote(self, pathname):
        self.db.execute("""
        --sql
        DELETE FROM remotes WHERE pathname=:pathname;
        """, [pathname])
        self.db.commit()

    def getArticles(self):
        # you can iterate over a cursor
        return self.db.execute('SELECT * FROM articles')

    def viewRefid(self, refid):
        with RefLog.getVersion(self.db, refid) as _version:
            return _version.read()

    def getHistory(self, refid):
        return RefLog.getHistory(self.db, refid)

    def getDetailedHistory(self, refid, pathname):
        return RefLog.getDetailedHistory(self.db, refid, pathname)

    def _createPatch(self, ffrom, fto, fpatch):
        detools.create_patch(ffrom=ffrom, fto=fto,
                             fpatch=fpatch,
                             compression='zstd',
                             use_mmap=False,
                             match_score=0,
                             patch_type='hdiffpatch',
                             algorithm='hdiffpatch')

    def _addNewArticleRef(self, refid, pathname):
        with io.BytesIO(b'') as ffrom, open(pathname, 'rb') as fto, self.path.joinpath('refs', refid).open('wb') as fpatch:
            self._createPatch(ffrom, fto, fpatch)

    def _addArticleRef(self, prefid, crefid, pathname):
        with RefLog.getVersion(self.db, prefid) as ffrom, open(pathname, 'rb') as fto, self.path.joinpath('refs', crefid).open('wb') as fpatch:
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
