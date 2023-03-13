from sigil.editingInterfaces.FileSystem import FileSystem


def checkout(pathname: str):
    sfs = FileSystem(pathname)
    return sfs.checkoutArticles()
