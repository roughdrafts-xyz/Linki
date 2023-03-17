import unittest
from sigil.data.ref import RefDetail
from sigil.article.repository import MemoryArticleRepository


class TestArticleRepository(unittest.TestCase):
    def setUp(self):
        self.remote = MemoryArticleRepository()

    def test_does_add_and_get_article(self):
        helloWorld = b'Hello World'
        refId = self.remote.add_article(helloWorld)
        expected = helloWorld
        actual = self.remote.get_article(refId)
        self.assertEqual(expected, actual)

    def test_does_update_article_and_get_details(self):
        helloWorld = b'Hello World'
        goodnightMoon = b'Goodnight Moon'

        prefId = self.remote.add_article(helloWorld)
        refId = self.remote.update_article(refId=prefId, content=goodnightMoon)

        expected = RefDetail(refId=refId, prefId=prefId)
        actual = self.remote.get_details(refId)

        self.assertEqual(expected, actual)
        self.assertNotEqual(expected.refId, expected.prefId)

    def test_does_create_and_gets_refs(self):
        helloWorld = b'Hello World'
        goodnightMoon = b'Goodnight Moon'

        prefId = self.remote.add_article(helloWorld)
        refId = self.remote.update_article(refId=prefId, content=goodnightMoon)

        ids = self.remote.get_refs()
        self.assertCountEqual({prefId, refId}, ids)
