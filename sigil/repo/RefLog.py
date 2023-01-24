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

    def applyHistory(self):
        history = self.getHistory()
        for row in history:
            with open('.sigil/refs/'+row['refid'], 'rb') as _file:
                detools.apply_patch(
                    ffrom=self.file,
                    fpatch=_file,
                    fto=self.file
                )

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
        SELECT refid FROM related_edit WHERE refid!='0' ORDER BY idx DESC
        --endsql
        ''', [self.refid])
