import shutil
import os
from sigil.editingInterfaces.FileSystem import FileSystem
from sigil.repo.Repo import Repo


class LocalCopy():
    def __init__(self, src):
        self.src = src
        self.srcRepoRefs = src+'/.sigil/refs/'
        self.srcRepoDB = src+'/.sigil/sigil.db'

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

        repo = Repo(bare=bare)
        repo.addRemote(self.src)

        if not bare:
            sfs = FileSystem()
            sfs.checkoutArticles()

        os.chdir(owd)
