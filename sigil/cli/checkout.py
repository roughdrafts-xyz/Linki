from sigil.cli.ShadowFileSystem import ShadowFileSystem
from sigil.repo.Repo import Repo


def checkout():
    sfs = ShadowFileSystem()
    db = Repo()
    articles = db.getArticles()
    sfs.loadFiles(articles)
