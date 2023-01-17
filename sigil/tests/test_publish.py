
import unittest
from sigil.tests.helpers import getInitializedDirectory
import os
from glob import glob


class TestPublishCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getInitializedDirectory()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_file_structure(self):
        files = glob(pathname='**', recursive=True, include_hidden=True)
        self.assertIn('.sigil', files)
        self.assertIn('.sigil/sigil.db', files)


if __name__ == '__main__':
    unittest.main(buffer=True)
