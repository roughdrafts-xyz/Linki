
import unittest
import os
from sigil.tests.helpers import getPopulatedDirectory
from sigil.cli.commands.publish import publish
from sigil.repo.Repo import Repo


class TestPublishCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getPopulatedDirectory()
        os.chdir(self.dir.name)
        self.db = Repo()
        self.db.connect()

    def tearDown(self):
        self.dir.cleanup()

    def test_does_publish(self):
        publish()
        articles = self.db.getArticles()
        fs_refs = os.listdir('.sigil/refs/')
        db_refs = [article["refid"] for article in articles]
        fs_refs.sort()
        db_refs.sort()
        self.assertEqual(fs_refs, db_refs)

    def test_does_not_publish_existing_articles(self):
        publish()
        publish()
        articles = self.db.getArticles()
        fs_refs = os.listdir('.sigil/refs/')
        db_refs = [article["refid"] for article in articles]
        fs_refs.sort()
        db_refs.sort()
        self.assertEqual(fs_refs, db_refs)

    def test_does_publish_new_articles_after_edit(self):
        publish()
        file = open('hello_world.md', 'w')
        file.write('Goodnight Moon')
        file.close()
        publish()
        articles = self.db.getArticles()
        fs_refs = os.listdir('.sigil/refs/')
        db_refs = [article["refid"] for article in articles]
        fs_refs.sort()
        db_refs.sort()
        self.assertNotEqual(fs_refs, db_refs)
        for db_ref in db_refs:
            with self.subTest(deb_ref=db_ref):
                self.assertIn(db_ref, fs_refs)

    def test_does_publish_recognize_new_files_that_are_actually_edits(self):
        pass


if __name__ == '__main__':
    unittest.main(buffer=True)
