from sigil.repo.LocalRepo.LocalRepo import LocalRepo


def view(refid):
    repo = LocalRepo()
    return repo.viewRefid(refid)
