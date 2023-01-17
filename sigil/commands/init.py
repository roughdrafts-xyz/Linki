from sigil.repo.Repo import Repo


def init():
    repo = Repo()
    try:
        repo.init()
        print('.sigil directory initiated')
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)
