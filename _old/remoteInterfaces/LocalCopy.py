import shutil
import os
from sigili.editingInterfaces.FileSystem import FileSystem
from sigili.old_repo.LocalRepo.LocalRepo import LocalRepo
from pathlib import Path


class LocalCopy():
    def __init__(self, src, bare=False):
        if not bare:
            self.base = '.sigil'
        else:
            self.base = '.'

        self.src = Path(src).joinpath(self.base)
        self.srcRepoRefs = self.src.joinpath('refs')
        self.srcRepoDB = self.src.joinpath('sigil.db')
        self.srcRepo = LocalRepo(pathname=src, bare=bare)

    def clone(self, dst, bare=False):

        if not bare:
            dstRepoRefs = dst+'/.sigil/refs/'
            dstRepoDB = dst+'/.sigil/sigil.db'
        else:
            dstRepoRefs = dst+'/refs/'
            dstRepoDB = dst+'/sigil.db'

        shutil.copytree(self.srcRepoRefs, dstRepoRefs)
        shutil.copyfile(self.srcRepoDB, dstRepoDB)

        owd = os.getcwd()
        os.chdir(dst)

        repo = LocalRepo(pathname=dst, bare=bare)
        repo.addRemote(self.srcRepo)

        if not bare:
            sfs = FileSystem()
            sfs.checkoutArticles()

        os.chdir(owd)
