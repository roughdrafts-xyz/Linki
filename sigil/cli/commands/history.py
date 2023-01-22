from sigil.repo.Repo import Repo


def formatRow(row):
    # TODO do formatting
    return row


def getFormattedHistory(refid):
    repo = Repo()
    repo.connect()
    history = repo.getHistory(refid)
    return map(formatRow, history)
