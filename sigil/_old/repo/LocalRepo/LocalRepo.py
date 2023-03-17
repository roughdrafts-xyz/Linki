import detools
import sqlite3
import hashlib
import io
import os
from sigil.old_repo.RefItem import RefItem
from sigil.old_repo.RemoteItem import RemoteItem
from sigil.old_repo.abc.Repo import Repo
from sigil.old_repo.LocalRepo.init import getRepoPath
from sigil.old_repo.LocalRepo.LocalRefLog import LocalRefLog
from sigil.old_repo.backports.file_digest import file_digest


class LocalRepo(Repo):

    def __init__(self, pathname: str, bare: bool = False):
        # TODO remote the bare options from this and just make getRepoPath automatically determine that. Testing shouldn't be too heavily effected since that'll still have init_repo to set things as bare.
        self.path = getRepoPath(pathname=pathname, bare=bare)
        dbPath = self.path.joinpath('sigil.db')
        dbPathString = f"file:{dbPath}"
        self.db = sqlite3.connect(dbPathString, uri=True)
        self.db.row_factory = sqlite3.Row
        self._refLog = LocalRefLog(self.db, self.path)

    @property
    def refLog(self):
        return self._refLog

    @property
    def remotePath(self):
        return self.path

    @property
    def remoteStyle(self):
        # TODO This method might lead to conflicts later.
        return "local"

    # I guess this should always return a set since refs should never be duplicates?
    def getRefIds(self) -> set:
        return set(os.listdir(self.path.joinpath('refs')))

    def _buildRemote(self, row):
        return RemoteItem(row.path, row.type)

    # TODO need to do a list comprehension to make this correct to the standard.
    def getRemotes(self) -> list[RemoteItem]:
        rows = self.db.execute('SELECT pathname, type FROM remotes')
        items = map(self._buildRemote, rows)
        return list(items)

    def addRemote(self, remote: Repo):
        pathname = remote.remotePath
        style = remote.remoteStyle
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

    def _getRefItem(self, row) -> RefItem:
        return RefItem(
            refId=row['refid'],
            pathName=row['pathname']
        )

    def getArticlesRefItems(self) -> list[RefItem]:
        # you can iterate over a cursor
        rows = self.db.execute('SELECT * FROM articles')
        return list(map(self._getRefItem, rows))

    def viewRefid(self, refid):
        with self.refLog.getVersion(refid) as _version:
            return _version.read()

    def getHistory(self, refid):
        return self.refLog.getHistory(refid)

    def getDetailedHistory(self, refid, pathname):
        return self.refLog.getDetailedHistory(refid, pathname)

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
        with self.refLog.getVersion(prefid) as ffrom, open(pathname, 'rb') as fto, self.path.joinpath('refs', crefid).open('wb') as fpatch:
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

    # TODO Temporary solution, see RefItem.py for more information.
    def _normalizePath(self, pathname):
        _path = self.path.joinpath(pathname)
        if not _path.exists() and not _path.is_file:
            return FileNotFoundError
        return str(_path.relative_to(self.path))

    def addNewArticle(self, pathname):
        pathname = self._normalizePath(pathname)
        fullPath = self.path.joinpath()
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
