import unittest

from sigil.article.repository import MemoryArticleRepository
from sigil.wiki import Wiki


class TestWiki(unittest.TestCase):
    def setUp(self):
        self.remote_articles = MemoryArticleRepository()
        self.local_articles = MemoryArticleRepository()
        self.wiki = Wiki([self.remote_articles, self.local_articles])

    def test_does_sync_without_history(self):
        self.remote_articles.add_article(b'Hello World')
        self.local_articles.add_article(b'Goodnight Moon')

        self.wiki.sync()

        self.assertCountEqual(
            self.local_articles._data,
            self.remote_articles._data
        )

        self.assertCountEqual(
            self.local_articles._log,
            self.remote_articles._log
        )

        pass
