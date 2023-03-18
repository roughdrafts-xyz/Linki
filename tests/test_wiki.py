import unittest
from test_article_repository import getRepository

from sigili.article.repository import FileSystemArticleRepository
from sigili.article.repository import MemoryArticleRepository
from sigili.wiki import Wiki


class TestWikiMemory(unittest.TestCase):
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


class TestWikiMixed(unittest.TestCase):
    def test_does_sync_without_history(self):
        with (
            getRepository(MemoryArticleRepository.__name__) as memory_articles,
            getRepository(FileSystemArticleRepository.__name__) as file_system_articles
        ):
            wiki = Wiki({memory_articles, file_system_articles})
            memory_articles.add_article(b'Hello World')
            file_system_articles.add_article(b'Goodnight Moon')

            wiki.sync()

            self.assertCountEqual(
                file_system_articles.get_refs(),
                memory_articles.get_refs()
            )

    def test_does_sync_with_history(self):
        with (
            getRepository(MemoryArticleRepository.__name__) as memory_articles,
            getRepository(FileSystemArticleRepository.__name__) as file_system_articles
        ):
            wiki = Wiki({memory_articles, file_system_articles})
            prefid_a = memory_articles.add_article(b'Hello Moon')
            prefid_b = file_system_articles.add_article(b'Hello Sun')
            memory_articles.update_article(
                refId=prefid_a,
                content=b'Goodnight Moon'
            )
            file_system_articles.update_article(
                refId=prefid_b,
                content=b'Goodnight Sun'
            )

            wiki.sync()

            self.assertCountEqual(
                file_system_articles.get_refs(),
                memory_articles.get_refs()
            )

    def test_does_sync_with_weird_history(self):
        """
        Weird history is defined as when two repositories incidentally create the same history through whatever means. This is meant to be usable with sneakernets, so this might happen from time to time.
        """
        with (
            getRepository(MemoryArticleRepository.__name__) as memory_articles,
            getRepository(FileSystemArticleRepository.__name__) as file_system_articles
        ):
            wiki = Wiki({memory_articles, file_system_articles})
            prefid = memory_articles.add_article(b'Hello Moon')
            file_system_articles.add_article(b'Hello Moon')
            memory_articles.update_article(
                refId=prefid,
                content=b'Goodnight Moon'
            )

            file_system_articles.update_article(
                refId=prefid,
                content=b'Goodnight Moon'
            )

            wiki.sync()

            self.assertCountEqual(
                file_system_articles.get_refs(),
                memory_articles.get_refs()
            )

    def test_does_clone_with_history(self):
        with (
            getRepository(MemoryArticleRepository.__name__) as memory_articles,
            getRepository(FileSystemArticleRepository.__name__) as file_system_articles
        ):
            wiki = Wiki({memory_articles, file_system_articles})
            prefid_a = memory_articles.add_article(b'Hello Moon')
            prefid_b = memory_articles.add_article(b'Hello Sun')
            memory_articles.update_article(
                refId=prefid_a,
                content=b'Goodnight Moon'
            )
            memory_articles.update_article(
                refId=prefid_b,
                content=b'Goodnight Sun'
            )

            wiki.sync()

            self.assertCountEqual(
                file_system_articles.get_refs(),
                memory_articles.get_refs()
            )
