import detools
from tempfile import TemporaryFile


def _modifyFile(refid, file):
    with open('.sigil/refs/'+refid, 'rb') as _file:
        detools.apply_patch(
            ffrom=file,
            fpatch=_file,
            fto=file
        )


def getVersion(db, refid):
    history = getHistory(db, refid)
    file = TemporaryFile('r+b')
    next(history)
    for row in history:
        print(dict(row))
        _modifyFile(row["refid"], file)
    return file


def getHistory(db, refid):
    return db.execute('''
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
    ''', [refid])
