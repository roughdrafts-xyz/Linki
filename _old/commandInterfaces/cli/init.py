import sqlite3
from sigili.old_repo.LocalRepo.init import init_repo, getRepoPath
from sigili.editingInterfaces.FileSystem import FileSystem


def init(pathname: str, bare=False):
    init_repo(pathname=pathname, bare=bare)
    path = getRepoPath(pathname=pathname, bare=bare)
    sqlite3.connect(path.joinpath('shadow_fs.db').resolve())

    sfs = FileSystem(pathname=pathname)
    sfs.refreshShadowFs()