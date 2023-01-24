from sigil.repo.Repo import Repo


def view(refid):
    repo = Repo()
    return repo.viewRefid(refid)
