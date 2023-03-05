from sigil.repo.LocalRepo.LocalRepo import Repo


def view(refid):
    repo = Repo()
    return repo.viewRefid(refid)
