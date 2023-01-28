import os
from glob import iglob
from sigil.editingInterfaces.FileSystem import FileSystem


def publish():
    sfs = FileSystem()

    files = iglob('**', recursive=True)
    count = [0, 0]
    for file in files:
        if not os.path.isfile(file):
            continue

        isNewFile = sfs.isNewFile(file)
        if (isNewFile):
            sfs.addNewFile(file)
            count[0] += 1
            continue

        inodeUpdated = sfs.hasInodeUpdated(file)
        if (inodeUpdated):
            sfs.updateExistingFile(file)
            count[1] += 1
            continue

    return count
