import os
import unittest
from sigil.commandInterfaces.cli.publish import publish
from sigil.repo.LocalRepo.LocalRepo import LocalRepo
from sigil.tests.helpers import getPopulatedDirectory
from sigil.editingInterfaces.FileSystem import FileSystem


class TestPublishCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getPopulatedDirectory()
        os.chdir(self.dir.name)
        self.sfs = FileSystem()
        self.db = self.sfs.repo

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
        with open('hello_world.md', 'w') as file:
            file.write('Goodnight Moon')
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

    def test_should_recreate_hashes(self):
        publish()
        original_refid = self.sfs.getRefid('hello_world.md')
        with open('hello_world.md', 'w') as file:
            file.write('Goodnight Moon')
        os.rename('hello_world.md', 'goodnight_moon.md')
        publish()
        edited_refid = self.sfs.getRefid('goodnight_moon.md')
        with open('hello_world.md', 'x') as file:
            file.write('Hello World!')
        publish()
        new_refid = self.sfs.getRefid('hello_world.md')
        self.assertNotEqual(original_refid, edited_refid)
        self.assertEqual(original_refid, new_refid)


if __name__ == '__main__':
    unittest.main(buffer=True)
