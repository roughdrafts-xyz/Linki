import sqlite3
from sigil.repo.Init import init_repo
from sigil.editingInterfaces.FileSystem import FileSystem


def init(quiet=False):
    try:
        init_repo()
        sqlite3.connect('.sigil/shadow_fs.db')

        sfs = FileSystem()
        sfs.refreshShadowFs()

        if not quiet:
            print('.sigil directory initiated')
    except FileExistsError:
        if not quiet:
            print('.sigil directory already exists.')
        exit(0)
