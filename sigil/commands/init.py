from sigil.repo.Repo import Repo


def init():
    repo = Repo()
    repo.init()
    print('.sigil directory initiated')
