import os
from sigili.editingInterfaces.FileSystem import FileSystem
from glob import iglob


def getStagedChanges(path='.'):
    sfs = FileSystem()

    updatedFiles = []
    if (os.path.isdir(path)):
        files = iglob('**', recursive=True)
        for file in files:
            if not os.path.isfile(file):
                continue

            inodeUpdated = sfs.hasInodeUpdated(file)
            if (inodeUpdated):
                updatedFiles.append(file)
                continue

            isNewFile = sfs.isNewFile(file)
            if (isNewFile):
                updatedFiles.append(file)
                continue
    else:
        if (sfs.hasInodeUpdated(path)):
            updatedFiles.append(path)
    return updatedFiles
