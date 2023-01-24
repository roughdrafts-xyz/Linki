from sigil.repo.Repo import Repo


def _formatHistoryRow(row):
    # TODO do formatting
    return row["refid"]


def getFormattedHistory(refid):
    repo = Repo()
    history = repo.getHistory(refid)
    return map(_formatHistoryRow, history)
