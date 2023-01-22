from sigil.workingDir.FileSystem import FileSystem
from sigil.repo.Repo import Repo


def checkout():
    sfs = FileSystem()
    db = Repo()
    db.connect()
    articles = db.getArticles()
    sfs.checkoutArticles(articles)
