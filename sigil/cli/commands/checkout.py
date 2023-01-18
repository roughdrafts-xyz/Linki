from sigil.cli._ShadowFileSystem import _ShadowFileSystem
from sigil.repo.Repo import Repo


def checkout():
    sfs = _ShadowFileSystem()
    db = Repo()
    articles = db.getArticles()
    sfs.loadFiles(articles)
