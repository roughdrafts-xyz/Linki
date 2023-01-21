from sigil.cli._ShadowFileSystem import _ShadowFileSystem
from sigil.repo.Repo import Repo


def checkout():
    sfs = _ShadowFileSystem()
    db = Repo()
    db.connect()
    articles = db.getArticles()
    sfs.checkoutArticles(articles)
