from sigil.old_repo.LocalRepo.LocalRepo import LocalRepo


def view(refid):
    repo = LocalRepo()
    return repo.viewRefid(refid)
