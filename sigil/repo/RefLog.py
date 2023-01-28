import detools
from io import BytesIO
from functools import lru_cache


@lru_cache(maxsize=1024)  # Based on the last number provided by Speed Test
def _modifyFile(prev, refid):
    with open('.sigil/refs/'+refid, 'rb') as _fpatch, BytesIO(prev) as _ffrom, BytesIO() as _fto:
        detools.apply_patch(
            ffrom=_ffrom,
            fpatch=_fpatch,
            fto=_fto
        )
        return _fto.getvalue()


def getVersion(db, refid):
    history = getHistory(db, refid)
    file = b''
    for row in history:
        file = _modifyFile(file, row["refid"])
    return BytesIO(file)


def getHistory(db, refid):
    history = db.execute('''
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
    next(history)  # Skips
    return history


def getDetailedHistory(db, refid, pathname):
    history = db.execute('''
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
