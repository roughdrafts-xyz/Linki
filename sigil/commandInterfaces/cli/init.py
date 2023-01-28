import sqlite3
from sigil.repo.Init import init_repo
from sigil.editingInterfaces.FileSystem import FileSystem


def init(exit_on_fail=True):
    init_repo()
    sqlite3.connect('.sigil/shadow_fs.db')

    sfs = FileSystem()
    sfs.refreshShadowFs()
