from sigil.repo.Repo import Repo


def view(refid):
    repo = Repo()
    repo.connect()
    return repo.viewRefid(refid)
