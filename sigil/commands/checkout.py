from .ShadowFileSystem import ShadowFileSystem
from .DbActions import DbActions


def checkout():
    sfs = ShadowFileSystem()
    db = DbActions()
    articles = db.getArticles()
    sfs.loadFiles(articles)
