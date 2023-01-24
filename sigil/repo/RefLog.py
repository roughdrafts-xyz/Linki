import detools
from tempfile import TemporaryFile


class RefLog():
    def __init__(self, refid, db):
        self.refid = refid
        self.db = db
        self.file = TemporaryFile('r+b')

    # This is a stub to make detools happy, it can be implemented more but there isn't a purpose for that yet.
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
        # TODO this needs to grab all the parents of refid and then return that as a cursor to iterate over
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
        SELECT refid FROM related_edit ORDER BY idx DESC
        --endsql
        ''', [self.refid])
