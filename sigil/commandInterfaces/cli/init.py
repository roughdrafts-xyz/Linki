from sigil.editingInterfaces.FileSystem import FileSystem


def init():
    try:
        sfs = FileSystem()
        sfs.init()
        sfs.connect()
        print('.sigil directory initiated')
    except FileExistsError:
        print('.sigil directory already exists.')
        exit(0)
