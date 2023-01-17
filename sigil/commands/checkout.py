from .ShadowFileSystem import ShadowFileSystem
from ..repo.Repo import Repo


def checkout():
    sfs = ShadowFileSystem()
    db = Repo()
    articles = db.getArticles()
    sfs.loadFiles(articles)
