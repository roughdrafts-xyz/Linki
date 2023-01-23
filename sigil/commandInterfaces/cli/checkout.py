from sigil.editingInterfaces.FileSystem import FileSystem
from sigil.repo.Repo import Repo


def checkout():
    sfs = FileSystem()
    sfs.connect()
    db = Repo()
    db.connect()
    articles = db.getArticles()
    sfs.checkoutArticles(articles)
