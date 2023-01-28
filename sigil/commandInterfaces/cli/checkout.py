from sigil.editingInterfaces.FileSystem import FileSystem


def checkout():
    sfs = FileSystem()
    return sfs.checkoutArticles()
