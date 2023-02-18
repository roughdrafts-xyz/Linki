import shutil
import os
from sigil.editingInterfaces.FileSystem import FileSystem


class LocalCopy():
    def __init__(self, src):
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
        if not bare:
            owd = os.getcwd()
            os.chdir(dst)
            sfs = FileSystem()
            sfs.checkoutArticles()
            os.chdir(owd)
