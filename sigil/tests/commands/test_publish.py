
import unittest
import os
from sigil.tests.helpers import getPopulatedDirectory
from sigil.commands.publish import publish
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
        articles = self.db.getArticles().fetchall()
        fs_refs = os.listdir('.sigil/refs/')
        db_refs = [article["refid"] for article in articles]
        self.assertEqual(fs_refs, db_refs)

    def test_does_publish_multiple_times(self):
        publish()
        publish()
        publish()
        articles = self.db.getArticles().fetchall()
        fs_refs = os.listdir('.sigil/refs/')
        db_refs = [article["refid"] for article in articles]
        self.assertEqual(fs_refs, db_refs)


if __name__ == '__main__':
    unittest.main(buffer=True)
