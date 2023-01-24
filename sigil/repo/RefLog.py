import detools
import contextlib
from tempfile import TemporaryFile


class RefLog(contextlib.AbstractContextManager):
    def __init__(self, db, refid):
        self.db = db
        self.file = TemporaryFile('r+b')
        self.refid = refid

    def __exit__(self, exc_type, exc, tb):
        return None

    def _modifyTempFile(self, refid):
        with open('.sigil/refs/'+refid, 'rb') as _file:
            detools.apply_patch(
                ffrom=self.file,
                fpatch=_file,
                fto=self.file
            )

    def applyHistory(self):
        history = self.getHistory()
        next(history)
        for row in history:
            print(dict(row))
            self._modifyTempFile(row["refid"])
        self._modifyTempFile(self.refid)

    def getHistory(self):
        return self.db.execute('''
        --sql
        WITH RECURSIVE
            related_edit(refid, idx) AS (
                VALUES(:refid, 0)
                UNION ALL
                SELECT edit_log.prefid, related_edit.idx+1 
                FROM edit_log JOIN related_edit
                ON edit_log.crefid = related_edit.refid
            )
        SELECT refid, idx FROM related_edit ORDER BY idx DESC
        --endsql
        ''', [self.refid])
