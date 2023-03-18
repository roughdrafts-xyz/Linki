from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator
from unittest import TestCase
from sigil.article.repository import ArticleRepository
from sigil.article.repository import MemoryArticleRepository
from sigil.article.repository import FileSystemArticleRepository
from sigil.article.repository import BadArticleRepository
from sigil.data.ref import RefDetail


@contextmanager
def getRepository(style: str) -> Generator:
    match style:
        case MemoryArticleRepository.__name__:
            yield MemoryArticleRepository()
        case BadArticleRepository.__name__:
            yield BadArticleRepository()
        case FileSystemArticleRepository.__name__:
            dir = TemporaryDirectory()
            try:
                yield FileSystemArticleRepository(path=Path(dir.name))
            finally:
                dir.cleanup()


class TestArticleRepository(TestCase):
    def setUp(self):
        self.styles = {
            MemoryArticleRepository.__name__,
            FileSystemArticleRepository.__name__,
            # BadArticleRepository.__name__,
        }

    def test_does_add_and_get_article(self):
        helloWorld = b'Hello World'
        expected = helloWorld
        for style in self.styles:
            with self.subTest(style=style), getRepository(style) as remote:
                refId = remote.add_article(helloWorld)
                actual = remote.get_article(refId)
                self.assertEqual(expected, actual)

    def test_does_update_article_and_get_details(self):
        helloWorld = b'Hello World'
        goodnightMoon = b'Goodnight Moon'

        for style in self.styles:
            with self.subTest(style=style), getRepository(style) as remote:
                prefId = remote.add_article(helloWorld)
                refId = remote.update_article(
                    refId=prefId, content=goodnightMoon)

                expected = RefDetail(refId=refId, prefId=prefId)
                actual = remote.get_details(refId)

                self.assertEqual(expected, actual)
                self.assertNotEqual(expected.refId, expected.prefId)

    def test_does_create_and_gets_refs(self):
        helloWorld = b'Hello World'
        goodnightMoon = b'Goodnight Moon'
        for style in self.styles:
            with self.subTest(style=style), getRepository(style) as remote:
                prefId = remote.add_article(helloWorld)
                refId = remote.update_article(
                    refId=prefId, content=goodnightMoon)

                ids = remote.get_refs()
                self.assertCountEqual({prefId, refId}, ids)
                self.assertNotEqual(refId, prefId)
