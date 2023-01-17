from sigil.repo.Repo import Repo
from sigil.cli.ShadowFileSystem import ShadowFileSystem


def init():
    repo = Repo()
    sfs = ShadowFileSystem()
    try:
        repo.init()
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)

    sfs.init()
    print('.sigil directory initiated')
