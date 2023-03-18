from sigili.editingInterfaces.FileSystem import FileSystem


def _formatHistoryRow(row):
    refid = row["refid"]
    pathname = row["pathname"]
    return f'{refid[0:6]}\t{pathname}'


def getFormattedHistory(pathname):
    sfs = FileSystem()
    repo = sfs.repo
    refid = sfs.getRefid(pathname)
    history = repo.getDetailedHistory(refid, pathname)
    return map(_formatHistoryRow, history)
