from sigil.repo.Repo import Repo
from sigil.editingInterfaces.FileSystem import FileSystem


def init():
    repo = Repo()
    sfs = FileSystem()
    try:
        repo.init()
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)

    sfs.init()
    print('.sigil directory initiated')
