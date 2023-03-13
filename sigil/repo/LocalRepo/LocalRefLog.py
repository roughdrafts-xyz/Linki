import detools
from pathlib import Path
from io import BytesIO
from functools import lru_cache

from sigil.repo.RefItem import RefItem
from sigil.repo.abc.RefLog import RefLog


class LocalRefLog(RefLog):
    def __init__(self, db, path: Path):
        self.db = db
        self.path = path

    def getRefItem(self, refid) -> RefItem:
        pathName = str(self.path.resolve())
        refBytes = self.path.joinpath('refs', refid).read_bytes()
        prefId = self._getPrefId(refid)
        return RefItem(refid, prefId, pathName, refBytes)

    def _getPrefId(self, refid: str) -> str:
        return ""

    def addRefItem(self, refItem: RefItem):
        return super().addRefItem(refItem)

    @lru_cache(maxsize=1024)  # Based on the last number provided by Speed Test
    def _modifyFile(self, prev, refid):
        with open(self.path.joinpath('refs', refid), 'rb') as _fpatch, BytesIO(prev) as _ffrom, BytesIO() as _fto:
            detools.apply_patch(
                ffrom=_ffrom,
                fpatch=_fpatch,
                fto=_fto
            )
            return _fto.getvalue()

    def getVersion(self, refid):
        history = self.getHistory(refid)
        file = b''
        for row in history:
            file = self._modifyFile(file, row["refid"])
        return BytesIO(file)

    def getHistory(self, refid):
        history = self.db.execute('''
        --sql
        WITH RECURSIVE
            related_edit(refid, idx) AS (
                VALUES(:refid, 0)
                UNION ALL
                SELECT edit_log.prefid, related_edit.idx+1 
                FROM edit_log JOIN related_edit
                ON edit_log.crefid = related_edit.refid
            )
        SELECT refid FROM related_edit ORDER BY idx DESC
        --endsql
        ''', [refid])
        next(history)  # Skips
        return history

    def getDetailedHistory(self, refid, pathname):
        history = self.db.execute('''
        --sql
        WITH RECURSIVE
            related_edit(refid, pathname, idx) AS (
                VALUES(:refid, :pathname, 0)
                UNION ALL
                SELECT edit_log.prefid, refid_info.pathname, related_edit.idx+1
                FROM edit_log 
                JOIN related_edit 
                ON edit_log.crefid = related_edit.refid
                JOIN refid_info 
                ON related_edit.refid = refid_info.refid
            )
        SELECT refid, pathname FROM related_edit ORDER BY idx DESC
        --endsql
        ''', [refid, pathname])
        next(history)
        return history
