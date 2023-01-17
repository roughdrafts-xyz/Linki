import unittest
import os
from glob import glob
from sigil.tests.helpers import getInitializedDirectory


class TestInitCommand(unittest.TestCase):
    def setUp(self):
        self.dir = getInitializedDirectory()
        os.chdir(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def test_file_structure(self):
        files = glob(pathname='**', recursive=True, include_hidden=True)
        self.assertEqual(files, ['.sigil', '.sigil/sigil.db'])


if __name__ == '__main__':
    unittest.main(buffer=True)
