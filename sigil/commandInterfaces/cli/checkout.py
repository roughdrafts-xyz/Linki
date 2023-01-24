from sigil.editingInterfaces.FileSystem import FileSystem


def checkout():
    sfs = FileSystem()
    sfs.checkoutArticles()
