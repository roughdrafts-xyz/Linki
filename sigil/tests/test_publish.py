
import unittest
import os
from sigil.tests.helpers import getPopulatedDirectory
from sigil.commands.publish import publish
from sigil.commands.DbActions import DbActions


class TestPublishCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getPopulatedDirectory()
        os.chdir(self.dir.name)
        self.db = DbActions()
        self.db.connect()

    def tearDown(self):
        self.dir.cleanup()

    def test_does_publish(self):
        publish()
        articles = self.db.getArticles().fetchall()
        refs = os.listdir('.sigil/refs/')
        for article in articles:
            with self.subTest(article=article):
                self.assertIn(article["refid"], refs)


if __name__ == '__main__':
    unittest.main(buffer=True)
