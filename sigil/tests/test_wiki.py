import unittest

from sigil.article.repository import MemoryArticleRepository
from sigil.wiki import Wiki


class TestWiki(unittest.TestCase):
    def setUp(self):
        self.remote_articles = MemoryArticleRepository()
        self.local_articles = MemoryArticleRepository()
        self.wiki = Wiki({self.remote_articles, self.local_articles})

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

    def test_does_sync_with_history(self):
        rprefid = self.remote_articles.add_article(b'Hello Moon')
        lprefid = self.local_articles.add_article(b'Hello Sun')
        self.remote_articles.update_article(
            refId=rprefid,
            content=b'Goodnight Moon'
        )
        self.local_articles.update_article(
            refId=lprefid,
            content=b'Goodnight Sun'
        )

        self.wiki.sync()

        self.assertCountEqual(
            self.local_articles._data,
            self.remote_articles._data
        )

        self.assertCountEqual(
            self.local_articles._log,
            self.remote_articles._log
        )

    def test_does_sync_with_weird_history(self):
        """
        Weird history is defined as when two repositories incidentally create the same history through whatever means. This is meant to be usable with sneakernets, so this might happen from time to time.
        """
        prefid = self.remote_articles.add_article(b'Hello Moon')
        self.local_articles.add_article(b'Hello Moon')
        self.remote_articles.update_article(
            refId=prefid,
            content=b'Goodnight Moon'
        )

        self.local_articles.update_article(
            refId=prefid,
            content=b'Goodnight Moon'
        )

        self.wiki.sync()

        self.assertCountEqual(
            self.local_articles._data,
            self.remote_articles._data
        )

        self.assertCountEqual(
            self.local_articles._log,
            self.remote_articles._log
        )
