from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from sigili.article.data.repository import MemoryArticleDataRepository
from sigili.article.data.repository import FileSystemArticleDataRepository
from sigili.article.data.repository import BadArticleDataRepository
from sigili.data.ref import RefDetail


@contextmanager
def getRepository(style: str):
    match style:
        case MemoryArticleDataRepository.__name__:
            yield MemoryArticleDataRepository()
        case BadArticleDataRepository.__name__:
            yield BadArticleDataRepository()
        case FileSystemArticleDataRepository.__name__:
            _dir = TemporaryDirectory()
            _dirPath = Path(_dir.name)
            FileSystemArticleDataRepository.initialize_directory(_dirPath)
            try:
                yield FileSystemArticleDataRepository(path=_dirPath)
            finally:
                _dir.cleanup()


class TestArticleRepositoryStyles(TestCase):
    styles = {
        MemoryArticleDataRepository.__name__,
        FileSystemArticleDataRepository.__name__,
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
                expected = {prefId, refId}
                self.assertCountEqual(expected, ids)
                self.assertNotEqual(refId, prefId)
