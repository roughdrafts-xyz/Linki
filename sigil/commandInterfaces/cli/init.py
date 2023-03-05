import sqlite3
from sigil.repo.LocalRepo.init import init_repo, getRepoPath
from sigil.editingInterfaces.FileSystem import FileSystem


def init(pathname=None, bare=False):
    init_repo(pathname=pathname, bare=bare)
    path = getRepoPath(pathname=pathname, bare=bare)
    sqlite3.connect(path.joinpath('shadow_fs.db').resolve())

    sfs = FileSystem()
    sfs.refreshShadowFs()
